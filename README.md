# UAReady — Email & Domain Validation System

> "The same email address. Working everywhere — in every language."

A Python library and REST API for validating internationalized email addresses and domain names. Built for the UA Adaptation Hackathon Nepal 2026.

Works with addresses like:

- `राम@नेपाल.नेपाल`
- `علي@مثال.إختبار`
- `用户@例子.广告`
- `test8@क्यान.संगठन`

---

## Why

The internet was built for ASCII. Most systems today still reject perfectly valid Nepali, Arabic, or Chinese email addresses. This project validates them correctly — using the actual standards, not workarounds.

---

## What it does

- Validates internationalized email addresses (RFC 6531 SMTPUTF8, RFC 6532 EAI)
- Validates IDN domain names (IDNA2008, UTS#46)
- Converts between Unicode and punycode/ACE form
- Applies NFC normalization before any checks
- Returns localized error messages in English, Nepali, and Arabic
- Checks if an SMTP server actually supports SMTPUTF8
- Can send a live test email over SMTPUTF8

---

## Standards

| Standard | RFC | What it covers |
|---|---|---|
| SMTPUTF8 | RFC 6531 | UTF-8 in SMTP envelope |
| EAI | RFC 6532 | Unicode in email local part |
| IDNA2008 | RFC 5891 | Internationalized domain names |
| UTS#46 | Unicode | IDNA compatibility processing |
| NFC | Unicode Annex #15 | Unicode normalization |
| DNS limits | RFC 1035 | Label <= 63 bytes, domain <= 253 chars |
| SMTP limits | RFC 5321 | Local part <= 64 bytes |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│                                                             │
│   Browser Demo          curl / any HTTP client              │
│  static/index.html   POST /api/validate/email               │
│  (HTML + vanilla JS)  POST /api/validate/domain             │
│  3 UI languages       POST /api/validate/batch              │
│  real-time calls      POST /api/smtp/capability             │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼──────────────────────────────┐
│                      main.py  (FastAPI)                     │
│  • CORS middleware                                          │
│  • mounts /api  → api/routes.py                             │
│  • mounts /     → static/index.html                         │
│  • /docs        → auto Swagger UI                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  api/  (routes + models)                    │
│  routes.py                  models.py                       │
│  • api_validate_email()     • EmailRequest                  │
│  • api_validate_domain()    • DomainRequest                 │
│  • api_validate_batch()     • BatchRequest                  │
│  • api_smtp_capability()    • SmtpCapabilityRequest         │
│  • api_smtp_send()          • SmtpSendRequest               │
└──────────────────────────────┬──────────────────────────────┘
                               │ calls
┌──────────────────────────────▼──────────────────────────────┐
│               validator/  (core library)                    │
│                                                             │
│  email_validator.py          domain_validator.py            │
│  ┌──────────────────────┐    ┌──────────────────────────┐   │
│  │ 1. NFC normalize     │    │ 1. NFC normalize          │   │
│  │ 2. control char check│    │ 2. strip trailing dot     │   │
│  │ 3. email-validator   │    │ 3. reject .  or  ..       │   │
│  │    (allow_smtputf8)  │    │ 4. idna.encode() → ACE    │   │
│  │ 4. local <= 64 bytes │    │ 5. label length checks    │   │
│  │ 5. → domain_validator│    │ 6. idna.decode() → Unicode│   │
│  │ 6. ace_email length  │    └──────────────────────────┘   │
│  └──────────────────────┘                                   │
│                                                             │
│  normalization.py     script_detector.py    errors.py       │
│  • nfc_normalize()    • detect_scripts()    • get_message() │
│  • has_control_chars()  (20+ Unicode        en / ne / ar    │
│                          script ranges)                     │
└──────────────────────────────┬──────────────────────────────┘
                               │ uses
┌──────────────────────────────▼──────────────────────────────┐
│                    Third-party libraries                    │
│   email-validator   idna (3.x)    smtplib     unicodedata   │
│   RFC 6531/6532     IDNA2008      SMTP test   NFC / script  │
│   EAI parsing       UTS#46        (stdlib)    (stdlib)      │
└─────────────────────────────────────────────────────────────┘
```

Data flow for `राम@नेपाल.नेपाल`:
1. `POST /api/validate/email` hits FastAPI
2. NFC normalize, then `email-validator` runs with `allow_smtputf8=True`
3. Local part byte-length checked (64 byte limit)
4. `idna.encode("नेपाल.नेपाल")` → `xn--l2bey1c2b.xn--l2bey1c2b`, label lengths checked
5. Scripts detected → `["Devanagari"]`
6. JSON response with valid flag, ACE form, standards list

---

## Project structure

```
UA_Adaptation_and_Hackathon/
│
├── main.py                    -- FastAPI app, mounts API + static
├── requirements.txt
│
├── validator/
│   ├── email_validator.py     -- core email validation logic
│   ├── domain_validator.py    -- IDNA2008 domain validation
│   ├── normalization.py       -- NFC + control char checks
│   ├── script_detector.py     -- detects Unicode scripts in input
│   └── errors.py              -- error messages in en/ne/ar
│
├── api/
│   ├── routes.py              -- route handlers
│   └── models.py              -- Pydantic models
│
├── static/
│   └── index.html             -- browser demo, works in 3 languages
│
└── tests/
    └── test_validator.py      -- 31 test cases
```

---

## Setup

```bash
git clone https://github.com/YOUR_TEAM/uaready-validator
cd uaready-validator

uv venv && uv pip install -r requirements.txt
uv run python main.py
```

Server starts at `http://localhost:8000`. Swagger docs at `/docs`.

---

## API

### POST /api/validate/email

```json
{ "email": "राम@नेपाल.नेपाल", "lang": "en" }
```

```json
{
  "valid": true,
  "normalized": "राम@नेपाल.नेपाल",
  "local_part": "राम",
  "domain": "नेपाल.नेपाल",
  "ace_email": "राम@xn--l2bey1c2b.xn--l2bey1c2b",
  "is_internationalized": true,
  "requires_smtputf8": true,
  "scripts_detected": ["Devanagari"],
  "standards": ["RFC 6531 (SMTPUTF8)", "RFC 6532 (EAI)", "Unicode NFC", "IDNA2008", "UTS#46"]
}
```

### POST /api/validate/domain

```json
{ "domain": "नेपाल.नेपाल" }
```

```json
{
  "valid": true,
  "ace_form": "xn--l2bey1c2b.xn--l2bey1c2b",
  "unicode_form": "नेपाल.नेपाल",
  "scripts_detected": ["Devanagari"]
}
```

### POST /api/validate/batch

Up to 50 emails or domains in one request.

```json
{
  "items": [
    { "type": "email",  "value": "राम@नेपाल.नेपाल" },
    { "type": "domain", "value": "مثال.مصر" }
  ],
  "lang": "ne"
}
```

### POST /api/smtp/capability

Connects to an SMTP server and checks if it advertises `SMTPUTF8`.

```json
{ "host": "mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e", "port": 25 }
```

### POST /api/smtp/send-test

Sends a real email over SMTPUTF8. Requires server credentials.

`lang` accepts `en`, `ne`, `ar`.

---

## Tests

```bash
uv run pytest tests/ -v
```

31 cases total:

Valid: `राम@नेपाल.नेपाल`, `محمد@مثال.مصر`, `user@example.com`, punycode domain, NFC-normalised input, ASCII local with IDN domain

Invalid: no `@`, empty local part, double `@@`, local > 64 bytes, double dot in domain, leading dot, empty domain

Domains — valid: Devanagari IDN, Arabic IDN, ASCII, punycode, subdomain, trailing-dot FQDN

Domains — invalid: double dot, leading dot, label > 63 chars, invalid IDNA character

---

## Scripts supported

| Script | Example |
|---|---|
| Devanagari (Nepali) | `राम@नेपाल.नेपाल` |
| Arabic | `علي@مثال.إختبار` |
| Chinese | `用户@例子.广告` |
| Latin | `user@example.com` |
| Mixed | `user.नाम@नेपाल.com` |

---

## Punycode reference

| Unicode | ACE / Punycode |
|---|---|
| `नेपाल.नेपाल` | `xn--l2bey1c2b.xn--l2bey1c2b` |
| `क्यान.संगठन` | `xn--11b2bu4dwd.xn--i1b6b1a6a2e` |
| `مثال.إختبار` | `xn--mgbh0fb.xn--kgbechtv` |
| `例子.广告` | `xn--fsq270a.xn--fiqs8s` |

---

## Live SMTPUTF8 test server

Provided by the hackathon for end-to-end testing:

```
Email:    test8@क्यान.संगठन
Username: mailbox10
Password: test8
Server:   mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e
```

---

## Nepal context

Nepal has had the `.नेपाल` ccTLD since 2014, but most validation libraries still reject it. Government portals, e-commerce, and onboarding systems all silently drop valid Nepali addresses. This tool is a reference implementation that gets it right.

---

## Known limitations

- No DNS/MX lookup by default — use `/api/smtp/capability` to check a live server
- Mixed-script domain labels are rejected (IDNA2008 requirement, not a bug)
- SMTP send needs credentials for an SMTPUTF8-capable server
- No bidi rendering validation

---

## Evaluation criteria

| Category | Weight |
|---|---|
| Standards Compliance | 30% |
| Technical Execution | 25% |
| Script Coverage | 20% |
| Nepal Relevance | 15% |
| Presentation | 10% |

---

## Team

| | Name |
|---|---|
| <img src="https://github.com/nushhkaa.png" width="50"> | [Anushka Bashyal](https://github.com/nushhkaa) |
| <img src="https://github.com/Indoorfinality.png" width="50"> | [Anushna Chaugain](https://github.com/Indoorfinality) |
| <img src="https://github.com/Coderkabish.png" width="50"> | [Kavish Dahal](https://github.com/Coderkabish) |
| <img src="https://github.com/DS-kj.png" width="50"> | [Kunjang Sherpa](https://github.com/DS-kj) |
| <img src="https://github.com/rishicares.png" width="50"> | [Rishikesh Gautam](https://github.com/rishicares) |
| <img src="https://github.com/bgprogrammer909.png" width="50"> | [Suchit Ratna Bajracharya](https://github.com/bgprogrammer909) |

---

MIT License
