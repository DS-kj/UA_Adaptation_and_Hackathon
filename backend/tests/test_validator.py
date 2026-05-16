import pytest
from validator import validate_email_address, validate_domain_name


# valid emails

class TestValidEmails:
    def test_devanagari_nepali(self):
        r = validate_email_address("राम@नेपाल.नेपाल")
        assert r["valid"], r.get("error")
        assert r["requires_smtputf8"] is True
        assert "Devanagari" in r["scripts_detected"]
        assert "RFC 6531 (SMTPUTF8)" in r["standards"]

    def test_devanagari_nepali_2(self):
        r = validate_email_address("सीता@डाक.नेपाल")
        assert r["valid"], r.get("error")
        assert r["is_internationalized"] is True

    def test_arabic_email(self):
        r = validate_email_address("محمد@مثال.مصر")
        assert r["valid"], r.get("error")
        assert r["requires_smtputf8"] is True
        assert any("Arabic" in s for s in r["scripts_detected"])

    def test_ascii_simple(self):
        r = validate_email_address("user@example.com")
        assert r["valid"], r.get("error")
        assert r["requires_smtputf8"] is False
        assert r["is_internationalized"] is False

    def test_ascii_complex(self):
        r = validate_email_address("user.name+tag@example.co.uk")
        assert r["valid"], r.get("error")

    def test_idn_domain_ascii_local(self):
        r = validate_email_address("info@नेपाल.नेपाल")
        assert r["valid"], r.get("error")

    def test_punycode_domain(self):
        r = validate_email_address("user@xn--l2bey1c2b.xn--l2bey1c2b")
        assert r["valid"], r.get("error")

    def test_nfc_normalization_applied(self):
        import unicodedata
        nfd_email = unicodedata.normalize("NFD", "user@exāmple.com")
        r = validate_email_address(nfd_email)
        assert r["valid"], r.get("error")


# invalid emails

class TestInvalidEmails:
    def test_no_at_sign(self):
        r = validate_email_address("notanemail")
        assert not r["valid"]
        assert "error" in r

    def test_empty_local_part(self):
        r = validate_email_address("@nodomain.com")
        assert not r["valid"]

    def test_double_at(self):
        r = validate_email_address("user@@double.com")
        assert not r["valid"]

    def test_empty_string(self):
        r = validate_email_address("")
        assert not r["valid"]

    def test_local_part_too_long(self):
        long_local = "a" * 65
        r = validate_email_address(f"{long_local}@example.com")
        assert not r["valid"]

    def test_domain_double_dot(self):
        r = validate_email_address("user@domain..com")
        assert not r["valid"]

    def test_domain_leading_dot(self):
        r = validate_email_address("user@.leadingdot.com")
        assert not r["valid"]

    def test_no_domain(self):
        r = validate_email_address("user@")
        assert not r["valid"]


# valid domains

class TestValidDomains:
    def test_devanagari_idn(self):
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
        r = validate_domain_name("xn--l2bey1c2b.xn--l2bey1c2b")
        assert r["valid"], r.get("error")

    def test_subdomain(self):
        r = validate_domain_name("mail.example.co.uk")
        assert r["valid"], r.get("error")
        assert r["label_count"] == 4

    def test_trailing_dot_fqdn(self):
        r = validate_domain_name("example.com.")
        assert r["valid"], r.get("error")


# invalid domains

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
        r = validate_domain_name("a" * 64 + ".com")
        assert not r["valid"]

    def test_invalid_idna_character(self):
        r = validate_domain_name("inv@lid.com")
        assert not r["valid"]


# localized error messages

class TestLocalizedErrors:
    def test_nepali_error_message(self):
        r = validate_email_address("notanemail", lang="ne")
        assert not r["valid"]
        assert any("ऀ" <= c <= "ॿ" for c in r["error"])

    def test_arabic_error_message(self):
        r = validate_domain_name("", lang="ar")
        assert not r["valid"]
        assert any("؀" <= c <= "ۿ" for c in r["error"])


# script detection

class TestScriptDetection:
    def test_mixed_script_email(self):
        r = validate_email_address("info@नेपाल.नेपाल")
        assert r["valid"], r.get("error")
        assert "Devanagari" in r["scripts_detected"]

    def test_pure_ascii_no_intl_script(self):
        r = validate_email_address("user@example.com")
        assert r["valid"]
        assert "Latin (ASCII)" in r["scripts_detected"]
