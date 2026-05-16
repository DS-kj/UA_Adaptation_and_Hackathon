import unicodedata


def nfc_normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


def has_control_chars(text: str) -> bool:
    return any(unicodedata.category(c) in ("Cc", "Cf") for c in text)
