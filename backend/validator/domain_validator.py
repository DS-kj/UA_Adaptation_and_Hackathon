import idna

from .errors import get_message
from .normalization import has_control_chars, nfc_normalize
from .script_detector import detect_scripts


def validate_domain_name(domain: str, lang: str = "en") -> dict:
    if not domain:
        return {"valid": False, "error": get_message("generic_domain", lang)}

    domain = nfc_normalize(domain)

    # strip trailing dot — FQDN notation is fine
    if domain.endswith(".") and len(domain) > 1:
        domain = domain[:-1]

    if has_control_chars(domain):
        return {"valid": False, "error": get_message("control_char", lang)}

    if domain.startswith(".") or ".." in domain:
        return {"valid": False, "error": get_message("empty_label", lang)}

    try:
        ace_bytes = idna.encode(domain)
        ace_domain = ace_bytes.decode("ascii")
    except idna.IDNAError as exc:
        return {"valid": False, "error": get_message("idna_error", lang, detail=str(exc))}
    except (UnicodeError, UnicodeDecodeError) as exc:
        return {"valid": False, "error": get_message("idna_error", lang, detail=str(exc))}

    if len(ace_domain) > 253:
        return {"valid": False, "error": get_message("domain_too_long", lang)}

    ace_labels = ace_domain.split(".")
    for label in ace_labels:
        if not label:
            return {"valid": False, "error": get_message("empty_label", lang)}
        if len(label) > 63:
            return {"valid": False, "error": get_message("label_too_long", lang)}

    try:
        unicode_form = idna.decode(ace_domain)
    except idna.IDNAError:
        unicode_form = domain

    scripts = detect_scripts(domain)

    return {
        "valid": True,
        "normalized": domain,
        "ace_form": ace_domain,
        "unicode_form": unicode_form,
        "labels": domain.split("."),
        "label_count": len(domain.split(".")),
        "scripts_detected": scripts,
        "is_internationalized": any(ord(c) > 127 for c in domain),
        "standards": ["IDNA2008", "UTS#46", "RFC 1035", "Unicode NFC"],
    }
