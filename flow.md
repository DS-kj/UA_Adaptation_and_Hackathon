# How the validation flow works

Using `राम@नेपाल.नेपाल` as the example throughout.

---

## The short version

Only the **domain** part gets converted to punycode. The local part (before `@`) stays as Unicode. DNS is ASCII-only, so the domain must be encoded. The local part only travels over SMTP, and RFC 6531 explicitly allows Unicode there.

```
राम@नेपाल.नेपाल
│         │
│         └── domain → converted to xn--l2bey1c2b.xn--l2bey1c2b
└── local  → stays as राम, never converted
```

---

## Step by step

### 1. NFC normalization

Before anything else, the input goes through Unicode NFC normalization. This collapses equivalent Unicode sequences into a single canonical form. For example, `ā` can be represented as one codepoint (U+0101) or as `a` + combining macron (two codepoints). NFC picks one. Without this, the same visible character could fail validation depending on how it was typed.

```
input → nfc_normalize() → normalized string
```

### 2. email-validator parses the address

The normalized string goes into the `email-validator` library with `allow_smtputf8=True`. It splits at `@`, checks the structure, and returns:

```
local_part = "राम"
domain     = "नेपाल.नेपाल"
smtputf8   = True   (because local part is non-ASCII)
```

If the split fails (no `@`, double `@`, empty local, etc.) it raises an error here and we're done.

### 3. Local part byte-length check

RFC 5321 says the local part must be at most 64 bytes. The `email-validator` library checks character count but not byte count, so we do it ourselves:

```python
local_bytes = "राम".encode("utf-8")  # 9 bytes (3 bytes per Devanagari char)
len(local_bytes) <= 64               # fine
```

If someone sends `aaaa...` (65 characters of ASCII) that's 65 bytes and fails. If someone sends 64 Devanagari chars, that's 192 bytes and fails too.

### 4. Domain conversion (where punycode happens)

The domain `नेपाल.नेपाल` goes into `validate_domain_name()`. Here's what happens:

```python
idna.encode("नेपाल.नेपाल")
# → b"xn--l2bey1c2b.xn--l2bey1c2b"
```

The `idna` library processes each dot-separated label independently:

```
नेपाल  →  punycode encode  →  l2bey1c2b  →  prepend xn--  →  xn--l2bey1c2b
  .                                                              .
नेपाल  →  punycode encode  →  l2bey1c2b  →  prepend xn--  →  xn--l2bey1c2b
```

The `xn--` prefix is the signal to DNS resolvers that the label is punycode-encoded. Resolvers that understand Unicode decode it; resolvers that don't still handle the ACE string as plain ASCII.

After encoding, we check:
- Total domain length <= 253 characters (DNS wire format limit)
- Each label <= 63 characters (RFC 1035)
- No empty labels (double dots, leading/trailing dots)

Then we decode back to Unicode for display:

```python
idna.decode("xn--l2bey1c2b.xn--l2bey1c2b")
# → "नेपाल.नेपाल"
```

### 5. Total email length check

RFC 5321 limits the full email address to 254 characters. We check the ACE form since that's what goes on the wire:

```
राम@xn--l2bey1c2b.xn--l2bey1c2b   →  39 characters, fine
```

### 6. Script detection

We scan every character's codepoint against known Unicode block ranges and report which scripts were found. This is informational — it doesn't affect validity.

```
राम@नेपाल.नेपाल  →  ["Devanagari"]
محمد@مثال.مصر     →  ["Arabic"]
user@example.com  →  ["Latin (ASCII)"]
info@नेपाल.नेपाल  →  ["Devanagari", "Latin (ASCII)"]
```

### 7. Response

```json
{
  "valid": true,
  "local_part": "राम",
  "domain": "नेपाल.नेपाल",
  "ace_email": "राम@xn--l2bey1c2b.xn--l2bey1c2b",
  "unicode_email": "राम@नेपाल.नेपाल",
  "requires_smtputf8": true,
  "is_internationalized": true,
  "scripts_detected": ["Devanagari"],
  "standards": ["RFC 6531 (SMTPUTF8)", "RFC 6532 (EAI)", "Unicode NFC", "IDNA2008", "UTS#46"]
}
```

---

## How punycode encoding works

Punycode (RFC 3492) encodes a Unicode string into ASCII using only letters, digits, and hyphens. The algorithm:

1. All ASCII characters in the label are copied as-is to the output
2. Non-ASCII codepoints are then encoded as a sequence of base-36 numbers appended after a `-` separator
3. The decoder knows where ASCII ends and the encoded part begins

For `नेपाल` (all non-ASCII, no ASCII chars in the label):
- There are no ASCII characters to copy first
- The five codepoints (0x928, 0x947, 0x92A, 0x93A, 0x932... approximately) get encoded into `l2bey1c2b`
- Result: `xn--l2bey1c2b`

For something like `münchen` (mixed):
- ASCII part `m-nchen` copied first (the umlaut is skipped in this pass)
- Then `ü` (U+00FC) is encoded and appended
- Result: `xn--mnchen-3ya`

---

## Why the local part is never converted

Punycode exists to bridge Unicode and DNS. The local part of an email address never goes near DNS — it's only handled by the SMTP server after the `@`. Two scenarios:

**Server supports SMTPUTF8** (RFC 6531): the server accepts UTF-8 in the SMTP envelope. You send `MAIL FROM:<राम@नेपाल.नेपाल>` literally and the server handles it. No conversion needed.

**Server does not support SMTPUTF8**: there is no fallback. You cannot send to `राम@नेपाल.नेपाल` from a non-SMTPUTF8 server. The address simply cannot be routed. This is why `requires_smtputf8: true` in the response is important — it tells you whether your sending server needs to support RFC 6531.

An address like `user@नेपाल.नेपाल` (ASCII local, IDN domain) does not require SMTPUTF8 — the local part is plain ASCII, and only the domain needs punycode for DNS. Any standard SMTP server can send it.

---

## Full code path

```
POST /api/validate/email  { "email": "राम@नेपाल.नेपाल" }
  │
  └── api/routes.py: api_validate_email()
        │
        └── validator/email_validator.py: validate_email_address()
              │
              ├── normalization.py: nfc_normalize()
              ├── normalization.py: has_control_chars()
              ├── email-validator library: validate_email(allow_smtputf8=True)
              │     splits → local="राम", domain="नेपाल.नेपाल"
              ├── byte-length check on local part
              │
              └── validator/domain_validator.py: validate_domain_name()
                    │
                    ├── normalization.py: nfc_normalize()
                    ├── idna.encode("नेपाल.नेपाल") → b"xn--l2bey1c2b.xn--l2bey1c2b"
                    ├── label length checks
                    ├── idna.decode(...) → "नेपाल.नेपाल"
                    └── script_detector.py: detect_scripts()
```

---

## Reference: some punycode conversions

| Unicode | ACE / Punycode |
|---|---|
| `नेपाल.नेपाल` | `xn--l2bey1c2b.xn--l2bey1c2b` |
| `क्यान.संगठन` | `xn--11b2bu4dwd.xn--i1b6b1a6a2e` |
| `مثال.مصر` | `xn--mgbh0fb.xn--wgbh1c` |
| `例子.广告` | `xn--fsq270a.xn--fiqs8s` |
| `münchen.de` | `xn--mnchen-3ya.de` |
