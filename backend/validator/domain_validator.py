import idna

from .errors import get_message
from .normalization import has_control_chars, nfc_normalize
from .script_detector import detect_scripts


def validate_domain_name(domain: str, lang: str = "en") -> dict:
    """
    Validate a domain name per IDNA2008 + UTS#46 + RFC 5321.

    Accepts both Unicode (नेपाल.नेपाल) and ACE (xn--...) forms.
    Returns a dict with 'valid' bool and detailed fields on success.
    """
    if not domain:
        return {"valid": False, "error": get_message("generic_domain", lang)}

    # NFC normalize first
    domain = nfc_normalize(domain)

    # Strip trailing dot (FQDN notation is fine, just normalize it away)
    if domain.endswith(".") and len(domain) > 1:
        domain = domain[:-1]

    if has_control_chars(domain):
        return {"valid": False, "error": get_message("control_char", lang)}

    # Reject obviously wrong forms early
    if domain.startswith(".") or ".." in domain:
        return {"valid": False, "error": get_message("empty_label", lang)}

    # Encode to ACE via IDNA2008 (idna.encode already enforces label length)
    try:
        ace_bytes = idna.encode(domain)
        ace_domain = ace_bytes.decode("ascii")
    except idna.IDNAError as exc:
        return {"valid": False, "error": get_message("idna_error", lang, detail=str(exc))}
    except (UnicodeError, UnicodeDecodeError) as exc:
        return {"valid": False, "error": get_message("idna_error", lang, detail=str(exc))}

    # DNS wire-format limit: 253 octets for the text representation
    if len(ace_domain) > 253:
        return {"valid": False, "error": get_message("domain_too_long", lang)}

    # Each label ≤ 63 octets (RFC 1035)
    ace_labels = ace_domain.split(".")
    for label in ace_labels:
        if not label:
            return {"valid": False, "error": get_message("empty_label", lang)}
        if len(label) > 63:
            return {"valid": False, "error": get_message("label_too_long", lang)}

    # Decode ACE back to Unicode for display
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
