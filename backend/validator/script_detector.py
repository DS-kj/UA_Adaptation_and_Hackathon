SCRIPT_RANGES: list[tuple[str, int, int]] = [
    ("Devanagari", 0x0900, 0x097F),
    ("Devanagari Extended", 0xA8E0, 0xA8FF),
    ("Arabic", 0x0600, 0x06FF),
    ("Arabic Supplement", 0x0750, 0x077F),
    ("Arabic Presentation Forms-A", 0xFB50, 0xFDFF),
    ("Arabic Presentation Forms-B", 0xFE70, 0xFEFF),
    ("CJK Unified Ideographs", 0x4E00, 0x9FFF),
    ("CJK Extension A", 0x3400, 0x4DBF),
    ("CJK Compatibility", 0xF900, 0xFAFF),
    ("Cyrillic", 0x0400, 0x04FF),
    ("Tamil", 0x0B80, 0x0BFF),
    ("Greek", 0x0370, 0x03FF),
    ("Hebrew", 0x0590, 0x05FF),
    ("Thai", 0x0E00, 0x0E7F),
    ("Bengali", 0x0980, 0x09FF),
    ("Gujarati", 0x0A80, 0x0AFF),
    ("Gurmukhi", 0x0A00, 0x0A7F),
    ("Kannada", 0x0C80, 0x0CFF),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Sinhala", 0x0D80, 0x0DFF),
    ("Myanmar", 0x1000, 0x109F),
    ("Khmer", 0x1780, 0x17FF),
    ("Mongolian", 0x1800, 0x18AF),
    ("Tibetan", 0x0F00, 0x0FFF),
]


def detect_scripts(text: str) -> list[str]:
    detected: set[str] = set()
    has_ascii_alpha = False

    for char in text:
        if char == "@" or char == ".":
            continue
        if char.isascii():
            if char.isalpha():
                has_ascii_alpha = True
            continue
        cp = ord(char)
        for script, start, end in SCRIPT_RANGES:
            if start <= cp <= end:
                detected.add(script)
                break

    if has_ascii_alpha:
        detected.add("Latin (ASCII)")

    return sorted(detected)
