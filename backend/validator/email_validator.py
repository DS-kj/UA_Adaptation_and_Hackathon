from email_validator import EmailNotValidError, validate_email

from .domain_validator import validate_domain_name
from .errors import get_message
from .normalization import has_control_chars, nfc_normalize
from .script_detector import detect_scripts


def validate_email_address(email: str, lang: str = "en") -> dict:
    if not email:
        return {"valid": False, "error": get_message("generic", lang)}

    original = email
    email = nfc_normalize(email)

    if has_control_chars(email):
        return {"valid": False, "error": get_message("control_char", lang)}

    try:
        info = validate_email(
            email,
            allow_smtputf8=True,
            allow_quoted_local=True,
            check_deliverability=False,
        )
    except EmailNotValidError as exc:
        raw = str(exc).lower()
        # check domain/IDNA errors first — their messages can contain "@" literally
        if "idna" in raw or ("domain" in raw and "empty" in raw):
            key = "empty_domain" if "empty" in raw else "invalid_domain"
        elif "domain" in raw:
            key = "invalid_domain"
        elif "local" in raw and ("empty" in raw or "too long" in raw):
            key = "empty_local" if "empty" in raw else "local_too_long"
        elif "at sign" in raw or "@" in raw:
            key = "missing_at"
        elif "control" in raw:
            key = "control_char"
        else:
            key = "generic"
        translated = get_message(key, lang)
        return {"valid": False, "error": translated if key != "generic" else str(exc)}

    local_part: str = info.local_part
    domain: str = info.domain

    # email-validator doesn't enforce the 64-byte local part limit from RFC 5321
    local_bytes = local_part.encode("utf-8")
    if len(local_bytes) > 64:
        return {"valid": False, "error": get_message("local_too_long", lang)}

    domain_result = validate_domain_name(domain, lang)
    if not domain_result["valid"]:
        return {"valid": False, "error": domain_result["error"]}

    ace_domain = domain_result["ace_form"]
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
