MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "missing_at": "Email must contain exactly one '@' symbol",
        "empty_local": "Local part (before @) cannot be empty",
        "empty_domain": "Domain (after @) cannot be empty",
        "local_too_long": "Local part exceeds 64 bytes (RFC 5321 limit)",
        "email_too_long": "Email address exceeds 254 characters",
        "domain_too_long": "Domain exceeds 253 characters in ACE/punycode form",
        "label_too_long": "Domain label exceeds 63 characters",
        "empty_label": "Domain contains an empty label — check for double dots or leading/trailing dots",
        "invalid_local_char": "Local part contains an invalid character",
        "idna_error": "Domain is not valid per IDNA2008: {detail}",
        "invalid_domain": "Domain is not a valid hostname",
        "control_char": "Input contains control characters which are not permitted",
        "generic": "Not a valid email address",
        "generic_domain": "Not a valid domain name",
    },
    "ne": {
        "missing_at": "इमेलमा ठ्याक्कै एउटा '@' चिह्न हुनुपर्छ",
        "empty_local": "स्थानीय भाग (@ अघि) खाली हुन सक्दैन",
        "empty_domain": "डोमेन (@ पछि) खाली हुन सक्दैन",
        "local_too_long": "स्थानीय भाग ६४ बाइटभन्दा लामो छ (RFC 5321 सीमा)",
        "email_too_long": "इमेल ठेगाना २५४ वर्णभन्दा लामो छ",
        "domain_too_long": "डोमेन ACE/punycode रूपमा २५३ वर्णभन्दा लामो छ",
        "label_too_long": "डोमेन लेबल ६३ वर्णभन्दा लामो छ",
        "empty_label": "डोमेनमा खाली लेबल छ — दोहोरो डट वा अगाडि/पछाडि डट जाँच गर्नुहोस्",
        "invalid_local_char": "स्थानीय भागमा अमान्य अक्षर छ",
        "idna_error": "डोमेन IDNA2008 अनुसार अमान्य छ: {detail}",
        "invalid_domain": "डोमेन मान्य होस्टनाम होइन",
        "control_char": "इनपुटमा नियन्त्रण अक्षरहरू छन् जुन अनुमति छैन",
        "generic": "मान्य इमेल ठेगाना होइन",
        "generic_domain": "मान्य डोमेन नाम होइन",
    },
    "ar": {
        "missing_at": "يجب أن يحتوي البريد الإلكتروني على رمز '@' واحد بالضبط",
        "empty_local": "لا يمكن أن يكون الجزء المحلي (قبل @) فارغاً",
        "empty_domain": "لا يمكن أن يكون النطاق (بعد @) فارغاً",
        "local_too_long": "الجزء المحلي يتجاوز 64 بايت",
        "email_too_long": "عنوان البريد الإلكتروني يتجاوز 254 حرفاً",
        "domain_too_long": "النطاق يتجاوز 253 حرفاً في شكل ACE",
        "label_too_long": "تسمية النطاق تتجاوز 63 حرفاً",
        "empty_label": "يحتوي النطاق على تسمية فارغة",
        "invalid_local_char": "يحتوي الجزء المحلي على حرف غير صالح",
        "idna_error": "النطاق غير صالح وفق IDNA2008: {detail}",
        "invalid_domain": "النطاق ليس اسم مضيف صالحاً",
        "control_char": "الإدخال يحتوي على أحرف تحكم غير مسموح بها",
        "generic": "عنوان بريد إلكتروني غير صالح",
        "generic_domain": "اسم نطاق غير صالح",
    },
}


def get_message(key: str, lang: str = "en", **kwargs: str) -> str:
    messages = MESSAGES.get(lang, MESSAGES["en"])
    msg = messages.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        try:
            msg = msg.format(**kwargs)
        except KeyError:
            pass
    return msg
