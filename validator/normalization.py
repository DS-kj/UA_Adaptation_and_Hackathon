import unicodedata


def nfc_normalize(text: str) -> str:
    """Apply NFC normalization per Unicode Standard Annex #15."""
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


def has_control_chars(text: str) -> bool:
    """Return True if text contains any control or format characters."""
    return any(unicodedata.category(c) in ("Cc", "Cf") for c in text)
