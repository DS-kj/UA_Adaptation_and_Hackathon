from email_validator import EmailNotValidError, validate_email

from .domain_validator import validate_domain_name
from .errors import get_message
from .normalization import has_control_chars, nfc_normalize
from .script_detector import detect_scripts


def validate_email_address(email: str, lang: str = "en") -> dict:
    """
    Validate an internationalised email address per:
      - RFC 6531 (SMTPUTF8) — non-ASCII local parts
      - RFC 6532 (EAI message format)
      - IDNA2008 — internationalised domain names
      - Unicode NFC normalisation

    Returns a dict with 'valid' bool and detailed fields on success.
    """
    if not email:
        return {"valid": False, "error": get_message("generic", lang)}

    # Step 1 — NFC normalise before any parsing
    original = email
    email = nfc_normalize(email)

    if has_control_chars(email):
        return {"valid": False, "error": get_message("control_char", lang)}

    # Step 2 — Use email-validator with SMTPUTF8 / EAI support
    try:
        info = validate_email(
            email,
            allow_smtputf8=True,       # RFC 6531 — non-ASCII local parts
            allow_quoted_local=True,   # RFC 5321 §4.1.2 quoted strings
            check_deliverability=False,  # skip DNS; we're validating format only
        )
    except EmailNotValidError as exc:
        # Translate the english error into the requested language where possible
        raw = str(exc).lower()
        if "at sign" in raw or "@" in raw:
            key = "missing_at"
        elif "local" in raw and ("empty" in raw or "too long" in raw):
            key = "empty_local" if "empty" in raw else "local_too_long"
        elif "domain" in raw and "empty" in raw:
            key = "empty_domain"
        elif "domain" in raw:
            key = "invalid_domain"
        elif "control" in raw:
            key = "control_char"
        else:
            key = "generic"
        # Fall back to the original english message if we have no translation
        translated = get_message(key, lang)
        return {"valid": False, "error": translated if key != "generic" else str(exc)}

    local_part: str = info.local_part
    domain: str = info.domain

    # Step 3 — Enforce RFC 5321 byte-length limit on the local part (email-validator skips this)
    local_bytes = local_part.encode("utf-8")
    if len(local_bytes) > 64:
        return {"valid": False, "error": get_message("local_too_long", lang)}

    # Step 4 — Independently validate the domain with IDNA2008 for stricter compliance
    domain_result = validate_domain_name(domain, lang)
    if not domain_result["valid"]:
        return {"valid": False, "error": domain_result["error"]}

    ace_domain = domain_result["ace_form"]
    # Total email length limit (RFC 5321 §4.5.3): 254 chars
    ace_email = f"{local_part}@{ace_domain}"
    if len(ace_email) > 254:
        return {"valid": False, "error": get_message("email_too_long", lang)}

    scripts = detect_scripts(email)
    is_intl = info.smtputf8 or any(ord(c) > 127 for c in email)

    standards = ["Unicode NFC", "IDNA2008", "UTS#46"]
    if is_intl:
        standards = ["RFC 6531 (SMTPUTF8)", "RFC 6532 (EAI)"] + standards

    return {
        "valid": True,
        "normalized": info.normalized,
        "local_part": local_part,
        "domain": domain,
        "ace_email": ace_email,
        "unicode_email": f"{local_part}@{domain_result['unicode_form']}",
        "is_internationalized": is_intl,
        "requires_smtputf8": info.smtputf8,
        "scripts_detected": scripts,
        "standards": standards,
    }
