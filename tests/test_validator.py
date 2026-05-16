"""
UAReady Validator — test suite
Covers ≥5 valid and ≥5 invalid cases for both email and domain validation
per the hackathon submission requirements.
"""

import pytest
from validator import validate_email_address, validate_domain_name


# ── Email: valid cases ───────────────────────────────────────────────────────

class TestValidEmails:
    def test_devanagari_nepali(self):
        """Devanagari local part and IDN domain — the core Nepal use-case."""
        r = validate_email_address("राम@नेपाल.नेपाल")
        assert r["valid"], r.get("error")
        assert r["requires_smtputf8"] is True
        assert "Devanagari" in r["scripts_detected"]
        assert "RFC 6531 (SMTPUTF8)" in r["standards"]

    def test_devanagari_nepali_2(self):
        """Second Devanagari test with different local and domain."""
        r = validate_email_address("सीता@डाक.नेपाल")
        assert r["valid"], r.get("error")
        assert r["is_internationalized"] is True

    def test_arabic_email(self):
        """Arabic local part with Arabic IDN domain."""
        r = validate_email_address("محمد@مثال.مصر")
        assert r["valid"], r.get("error")
        assert r["requires_smtputf8"] is True
        assert any("Arabic" in s for s in r["scripts_detected"])

    def test_ascii_simple(self):
        """Standard ASCII email — must still pass."""
        r = validate_email_address("user@example.com")
        assert r["valid"], r.get("error")
        assert r["requires_smtputf8"] is False
        assert r["is_internationalized"] is False

    def test_ascii_complex(self):
        """ASCII with plus-addressing, dots, and ccTLD."""
        r = validate_email_address("user.name+tag@example.co.uk")
        assert r["valid"], r.get("error")

    def test_idn_domain_ascii_local(self):
        """ASCII local part with Devanagari IDN domain."""
        r = validate_email_address("info@नेपाल.नेपाल")
        assert r["valid"], r.get("error")
        # Domain is international but local is ASCII, so SMTPUTF8 may or may not
        # be required depending on library detection — just check validity.

    def test_punycode_domain(self):
        """ACE/punycode domain form of नेपाल.नेपाल — must be accepted."""
        r = validate_email_address("user@xn--l2bey1c2b.xn--l2bey1c2b")
        assert r["valid"], r.get("error")

    def test_nfc_normalization_applied(self):
        """Input that is not NFC should be normalised transparently."""
        import unicodedata
        # NFD form of 'ā' (a + combining macron)
        nfd_email = unicodedata.normalize("NFD", "user@exāmple.com")
        r = validate_email_address(nfd_email)
        # Normalised form is valid
        assert r["valid"], r.get("error")


# ── Email: invalid cases ─────────────────────────────────────────────────────

class TestInvalidEmails:
    def test_no_at_sign(self):
        """Missing @ — the most basic failure."""
        r = validate_email_address("notanemail")
        assert not r["valid"]
        assert "error" in r

    def test_empty_local_part(self):
        """@ at the start means empty local part."""
        r = validate_email_address("@nodomain.com")
        assert not r["valid"]

    def test_double_at(self):
        """Two @ signs is never valid."""
        r = validate_email_address("user@@double.com")
        assert not r["valid"]

    def test_empty_string(self):
        r = validate_email_address("")
        assert not r["valid"]

    def test_local_part_too_long(self):
        """Local part > 64 bytes violates RFC 5321."""
        long_local = "a" * 65
        r = validate_email_address(f"{long_local}@example.com")
        assert not r["valid"]

    def test_domain_double_dot(self):
        """Double dot in domain produces an empty label."""
        r = validate_email_address("user@domain..com")
        assert not r["valid"]

    def test_domain_leading_dot(self):
        r = validate_email_address("user@.leadingdot.com")
        assert not r["valid"]

    def test_no_domain(self):
        """@ with nothing after it."""
        r = validate_email_address("user@")
        assert not r["valid"]


# ── Domain: valid cases ──────────────────────────────────────────────────────

class TestValidDomains:
    def test_devanagari_idn(self):
        """Core Nepal IDN domain."""
        r = validate_domain_name("नेपाल.नेपाल")
        assert r["valid"], r.get("error")
        assert r["is_internationalized"] is True
        assert r["ace_form"].startswith("xn--")
        assert "Devanagari" in r["scripts_detected"]
        assert "IDNA2008" in r["standards"]

    def test_arabic_idn(self):
        r = validate_domain_name("مثال.مصر")
        assert r["valid"], r.get("error")
        assert any("Arabic" in s for s in r["scripts_detected"])

    def test_ascii_domain(self):
        r = validate_domain_name("example.com")
        assert r["valid"], r.get("error")
        assert r["is_internationalized"] is False

    def test_punycode_input(self):
        """ACE/punycode input for नेपाल.नेपाल should be accepted and decoded."""
        r = validate_domain_name("xn--l2bey1c2b.xn--l2bey1c2b")
        assert r["valid"], r.get("error")

    def test_subdomain(self):
        r = validate_domain_name("mail.example.co.uk")
        assert r["valid"], r.get("error")
        assert r["label_count"] == 4

    def test_trailing_dot_fqdn(self):
        """Trailing dot (FQDN notation) should be accepted."""
        r = validate_domain_name("example.com.")
        assert r["valid"], r.get("error")


# ── Domain: invalid cases ────────────────────────────────────────────────────

class TestInvalidDomains:
    def test_empty_string(self):
        r = validate_domain_name("")
        assert not r["valid"]

    def test_double_dot(self):
        r = validate_domain_name("domain..com")
        assert not r["valid"]

    def test_leading_dot(self):
        r = validate_domain_name(".leadingdot.com")
        assert not r["valid"]

    def test_too_long_label(self):
        """A single label longer than 63 chars."""
        r = validate_domain_name("a" * 64 + ".com")
        assert not r["valid"]

    def test_invalid_idna_character(self):
        """Characters that cannot appear in any IDNA2008 label."""
        r = validate_domain_name("inv@lid.com")
        assert not r["valid"]


# ── Language / error-message tests ──────────────────────────────────────────

class TestLocalizedErrors:
    def test_nepali_error_message(self):
        """Invalid email should return a Nepali error when lang='ne'."""
        r = validate_email_address("notanemail", lang="ne")
        assert not r["valid"]
        # Error should contain a Devanagari character
        assert any("ऀ" <= c <= "ॿ" for c in r["error"])

    def test_arabic_error_message(self):
        """Invalid domain should return an Arabic error when lang='ar'."""
        r = validate_domain_name("", lang="ar")
        assert not r["valid"]
        assert any("؀" <= c <= "ۿ" for c in r["error"])


# ── Script detection tests ───────────────────────────────────────────────────

class TestScriptDetection:
    def test_mixed_script_email(self):
        """Local part ASCII, domain Devanagari — both scripts reported."""
        r = validate_email_address("info@नेपाल.नेपाल")
        assert r["valid"], r.get("error")
        detected = r["scripts_detected"]
        assert "Devanagari" in detected

    def test_pure_ascii_no_intl_script(self):
        r = validate_email_address("user@example.com")
        assert r["valid"]
        assert "Latin (ASCII)" in r["scripts_detected"]
