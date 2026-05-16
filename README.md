# UAReady — Email & Domain Validation System

> **“The same email address. Working everywhere — in every language.”**

Validate internationalized email addresses and Unicode domain names using modern internet standards including SMTPUTF8, EAI, IDNA2008, UTS#46, and Unicode NFC normalization.

Supports native-script email addresses such as:

- `राम@नेपाल.नेपाल`
- `علي@مثال.إختبار`
- `用户@例子.广告`
- `test8@क्यान.संगठन`

---

# 🌍 Why This Project Matters

The internet was originally built for ASCII-only text. That means millions of valid native-language email addresses are still rejected by modern systems.

UAReady solves this problem by enabling validation and normalization of:

- Nepali (Devanagari)
- Arabic
- Chinese
- Cyrillic
- Tamil
- Mixed Unicode + ASCII addresses

This project directly supports Nepal’s digital identity ecosystem through `.नेपाल` and `.संगठन` domains.

---

# ✨ Features

- ✅ Unicode email validation
- ✅ SMTPUTF8 detection (RFC 6531)
- ✅ EAI support (RFC 6532)
- ✅ IDNA2008 + UTS#46 domain encoding
- ✅ Punycode conversion
- ✅ Unicode NFC normalization
- ✅ Bilingual error messages (English + Nepali)
- ✅ Flask REST API
- ✅ CLI validator
- ✅ Automated test suite
- ⭐ MX record lookup (stretch goal)
- ⭐ Live SMTPUTF8 capability verification

---

# 📚 Standards Implemented

| Standard | RFC / Spec | Purpose |
|---|---|---|
| SMTPUTF8 | RFC 6531 | UTF-8 email transport support |
| EAI | RFC 6532 | Unicode local-part support |
| IDNA2008 | RFC 5891 | Internationalized domain handling |
| UTS#46 | Unicode | Compatibility processing |
| NFC | Unicode | Unicode normalization |

---

# 🏗️ System Architecture

```text
User Input
    │
    ▼
┌────────────────────┐
│ NFC Normalization  │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Parse Email (@)    │
└──────┬───────┬─────┘
       ▼       ▼
┌──────────┐ ┌────────────────┐
│ Local    │ │ Domain         │
│ Validator│ │ Validator      │
└────┬─────┘ └──────┬─────────┘
     ▼              ▼
┌──────────┐ ┌──────────────┐
│ SMTPUTF8│ │ Punycode     │
│ Detect   │ │ Encoding     │
└────┬─────┘ └──────┬───────┘
     ▼              ▼
       ┌──────────────────┐
       │ Validation Result│
       └──────────────────┘
```

---

# 📂 Project Structure

```text
uaready-validator/
│
├── README.md
├── requirements.txt
│
├── validator/
│   ├── __init__.py
│   ├── email_validator.py
│   ├── domain_validator.py
│   └── normalizer.py
│
├── api/
│   └── app.py
│
├── cli/
│   └── cli.py
│
├── demo/
│   └── index.html
│
├── tests/
│   └── test_cases.py
│
└── slides/
    └── presentation.pdf
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_TEAM/uaready-validator
cd uaready-validator
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 📦 Requirements

```txt
idna
dnspython
flask
flask-cors
```

---

# 🚀 Running the Project

## Run Flask API

```bash
python api.py
```

Server runs on:

```text
http://localhost:5000
```

---

# 📡 API Endpoint

## POST `/validate`

### Request

```json
{
  "email": "राम@नेपाल.नेपाल"
}
```

### Response

```json
{
  "valid": true,
  "normalized": "राम@नेपाल.नेपाल",
  "local": "राम",
  "domain": "नेपाल.नेपाल",
  "punycode": "xn--n2bm2a.xn--n2bm2a",
  "requires_smtputf8": true,
  "message": "Valid internationalized email ✓"
}
```

---

# 💻 CLI Usage

```bash
python cli.py "राम@नेपाल.नेपाल"
```

Example Output:

```text
✓ Valid internationalized email

Local Part: राम
Domain: नेपाल.नेपाल
Punycode: xn--n2bm2a.xn--n2bm2a
SMTPUTF8 Required: True
```

---

# 🧪 Running Tests

```bash
python tests/test_cases.py
```

---

# ✅ Supported Scripts

| Script | Example | Status |
|---|---|---|
| Devanagari | राम@नेपाल.नेपाल | ✅ Full |
| Arabic | علي@مثال.إختبار | ✅ Full |
| Chinese | 用户@例子.广告 | ✅ Full |
| Latin | user@example.com | ✅ Full |
| Mixed Unicode | user.नाम@नेपाल.com | ✅ Full |

---

# 🧪 Test Cases

## Valid Emails

| Email | Description |
|---|---|
| test8@क्यान.संगठन | Live SMTPUTF8 mailbox |
| राम@नेपाल.नेपाल | Nepali Unicode email |
| user@xn--n2bm2a.xn--n2bm2a | Punycode format |
| علي@مثال.إختبار | Arabic EAI |
| 用户@例子.广告 | Chinese EAI |

---

## Invalid Emails

| Email | Error |
|---|---|
| @नेपाल.नेपाल | Empty local part |
| राम@ | Empty domain |
| .राम@नेपाल.नेपाल | Starts with dot |
| राम@नेपाल | Missing TLD |
| राम@@नेपाल.नेपाल | Invalid format |
| राम..नाम@नेपाल.नेपाल | Consecutive dots |

---

# 🔍 Core Validation Rules

## Local Part Rules

- Cannot be empty
- Maximum 64 UTF-8 bytes
- Cannot start with `.`
- Cannot end with `.`
- Cannot contain consecutive dots

## Domain Rules

- Must contain a TLD
- Must be IDNA2008 encodable
- No leading/trailing dots
- Labels ≤ 63 bytes
- Total domain ≤ 253 chars

---

# 🌐 SMTPUTF8 Detection

```python
def requires_smtputf8(email: str) -> bool:
    return not email.isascii()
```

---

# 🔄 Punycode Conversion Examples

| Unicode Domain | Punycode |
|---|---|
| नेपाल.नेपाल | xn--n2bm2a.xn--n2bm2a |
| क्यान.संगठन | xn--11b2bu4dwd.xn--i1b6b1a6a2e |
| مثال.إختبار | xn--mgbh0fb.xn--kgbechtv |
| 例子.广告 | xn--fsq270a.xn--fiqs8s |

---

# 🇳🇵 Nepal Relevance

Nepal officially supports the `.नेपाल` ccTLD, but many systems still reject Nepali email addresses.

UAReady enables:

- Nepali-language digital identity
- Unicode email validation
- Government onboarding systems
- Native-script domain verification
- SMTPUTF8-ready infrastructure

This directly supports Nepal’s movement toward localized internet services and inclusive digital access.

---

# 📡 Live SMTPUTF8 Test Server

```text
Email: test8@क्यान.संगठन
Username: mailbox10
Password: test8
```

SMTPUTF8-compatible mail server:

```text
mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e
```

---

# 🛰️ SMTPUTF8 Capability Check

```python
import smtplib

with smtplib.SMTP('mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e') as s:
    features = s.esmtp_features
    print('SMTPUTF8 supported:', 'smtputf8' in features)
```

---

# 📈 Stretch Goals

- ⭐ Browser-based live validator
- ⭐ MX record lookup
- ⭐ Real SMTP send testing
- ⭐ Multi-script rendering validation
- ⭐ Docker deployment
- ⭐ Public validation API

---

# ⚠️ Known Limitations

- Bidi (RTL/LTR) rendering validation not implemented
- SMTP live delivery requires internet access
- Full mailbox existence verification not included
- Advanced Unicode spoof detection not implemented

---

# 🤝 Contributors

| Profile | Name |
|---|---|
| <img src="https://github.com/nushhkaa.png" width="80"> | [Anushka Bashyal](https://github.com/nushhkaa) |
| <img src="https://github.com/Indoorfinality.png" width="80"> | [Anushna Chaugain](https://github.com/Indoorfinality) |
| <img src="https://github.com/Coderkabish.png" width="80"> | [Kavish Dahal](https://github.com/Coderkabish) |
| <img src="https://github.com/DS-kj.png" width="80"> | [Kunjang Sherpa](https://github.com/DS-kj) |
| <img src="https://github.com/rishicares.png" width="80"> | [Rishikesh Gautam](https://github.com/rishicares) |
| <img src="https://github.com/bgprogrammer909.png" width="80"> | [Suchit Ratna Bajracharya](https://github.com/bgprogrammer909) |

---

# 🏆 Evaluation Focus

| Category | Weight |
|---|---|
| Standards Compliance | 30% |
| Technical Execution | 25% |
| Script Coverage | 20% |
| Nepal Relevance | 15% |
| Presentation | 10% |

---

# 🛠️ Technologies Used

- Python
- Flask
- idna
- dnspython
- Unicode NFC
- SMTPUTF8
- IDNA2008

---

# 🤝 Contributing

Contributions are welcome.

Ideas:
- Add more scripts
- Improve spoof detection
- Add GUI dashboard
- Improve DNS validation
- Add Docker support

---

# 📜 License

MIT License

---

# ❤️ Final Note

> “Language should never be a barrier to digital identity.”

UAReady helps make the internet more inclusive by enabling email validation in every language — starting with Nepal.# UAReady — Email & Domain Validation System

> **“The same email address. Working everywhere — in every language.”**

Validate internationalized email addresses and Unicode domain names using modern internet standards including SMTPUTF8, EAI, IDNA2008, UTS#46, and Unicode NFC normalization.

Supports native-script email addresses such as:

- `राम@नेपाल.नेपाल`
- `علي@مثال.إختبار`
- `用户@例子.广告`
- `test8@क्यान.संगठन`

---

# 🌍 Why This Project Matters

The internet was originally built for ASCII-only text. That means millions of valid native-language email addresses are still rejected by modern systems.

UAReady solves this problem by enabling validation and normalization of:

- Nepali (Devanagari)
- Arabic
- Chinese
- Cyrillic
- Tamil
- Mixed Unicode + ASCII addresses

This project directly supports Nepal’s digital identity ecosystem through `.नेपाल` and `.संगठन` domains.

---

# ✨ Features

- ✅ Unicode email validation
- ✅ SMTPUTF8 detection (RFC 6531)
- ✅ EAI support (RFC 6532)
- ✅ IDNA2008 + UTS#46 domain encoding
- ✅ Punycode conversion
- ✅ Unicode NFC normalization
- ✅ Bilingual error messages (English + Nepali)
- ✅ Flask REST API
- ✅ CLI validator
- ✅ Automated test suite
- ⭐ MX record lookup (stretch goal)
- ⭐ Live SMTPUTF8 capability verification

---

# 📚 Standards Implemented

| Standard | RFC / Spec | Purpose |
|---|---|---|
| SMTPUTF8 | RFC 6531 | UTF-8 email transport support |
| EAI | RFC 6532 | Unicode local-part support |
| IDNA2008 | RFC 5891 | Internationalized domain handling |
| UTS#46 | Unicode | Compatibility processing |
| NFC | Unicode | Unicode normalization |

---

# 🏗️ System Architecture

```text
User Input
    │
    ▼
┌────────────────────┐
│ NFC Normalization  │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Parse Email (@)    │
└──────┬───────┬─────┘
       ▼       ▼
┌──────────┐ ┌────────────────┐
│ Local    │ │ Domain         │
│ Validator│ │ Validator      │
└────┬─────┘ └──────┬─────────┘
     ▼              ▼
┌──────────┐ ┌──────────────┐
│ SMTPUTF8│ │ Punycode     │
│ Detect   │ │ Encoding     │
└────┬─────┘ └──────┬───────┘
     ▼              ▼
       ┌──────────────────┐
       │ Validation Result│
       └──────────────────┘
```

---

# 📂 Project Structure

```text
uaready-validator/
│
├── README.md
├── requirements.txt
│
├── validator/
│   ├── __init__.py
│   ├── email_validator.py
│   ├── domain_validator.py
│   └── normalizer.py
│
├── api/
│   └── app.py
│
├── cli/
│   └── cli.py
│
├── demo/
│   └── index.html
│
├── tests/
│   └── test_cases.py
│
└── slides/
    └── presentation.pdf
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_TEAM/uaready-validator
cd uaready-validator
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 📦 Requirements

```txt
idna
dnspython
flask
flask-cors
```

---

# 🚀 Running the Project

## Run Flask API

```bash
python api.py
```

Server runs on:

```text
http://localhost:5000
```

---

# 📡 API Endpoint

## POST `/validate`

### Request

```json
{
  "email": "राम@नेपाल.नेपाल"
}
```

### Response

```json
{
  "valid": true,
  "normalized": "राम@नेपाल.नेपाल",
  "local": "राम",
  "domain": "नेपाल.नेपाल",
  "punycode": "xn--n2bm2a.xn--n2bm2a",
  "requires_smtputf8": true,
  "message": "Valid internationalized email ✓"
}
```

---

# 💻 CLI Usage

```bash
python cli.py "राम@नेपाल.नेपाल"
```

Example Output:

```text
✓ Valid internationalized email

Local Part: राम
Domain: नेपाल.नेपाल
Punycode: xn--n2bm2a.xn--n2bm2a
SMTPUTF8 Required: True
```

---

# 🧪 Running Tests

```bash
python tests/test_cases.py
```

---

# ✅ Supported Scripts

| Script | Example | Status |
|---|---|---|
| Devanagari | राम@नेपाल.नेपाल | ✅ Full |
| Arabic | علي@مثال.إختبار | ✅ Full |
| Chinese | 用户@例子.广告 | ✅ Full |
| Latin | user@example.com | ✅ Full |
| Mixed Unicode | user.नाम@नेपाल.com | ✅ Full |

---

# 🧪 Test Cases

## Valid Emails

| Email | Description |
|---|---|
| test8@क्यान.संगठन | Live SMTPUTF8 mailbox |
| राम@नेपाल.नेपाल | Nepali Unicode email |
| user@xn--n2bm2a.xn--n2bm2a | Punycode format |
| علي@مثال.إختبار | Arabic EAI |
| 用户@例子.广告 | Chinese EAI |

---

## Invalid Emails

| Email | Error |
|---|---|
| @नेपाल.नेपाल | Empty local part |
| राम@ | Empty domain |
| .राम@नेपाल.नेपाल | Starts with dot |
| राम@नेपाल | Missing TLD |
| राम@@नेपाल.नेपाल | Invalid format |
| राम..नाम@नेपाल.नेपाल | Consecutive dots |

---

# 🔍 Core Validation Rules

## Local Part Rules

- Cannot be empty
- Maximum 64 UTF-8 bytes
- Cannot start with `.`
- Cannot end with `.`
- Cannot contain consecutive dots

## Domain Rules

- Must contain a TLD
- Must be IDNA2008 encodable
- No leading/trailing dots
- Labels ≤ 63 bytes
- Total domain ≤ 253 chars

---

# 🌐 SMTPUTF8 Detection

```python
def requires_smtputf8(email: str) -> bool:
    return not email.isascii()
```

---

# 🔄 Punycode Conversion Examples

| Unicode Domain | Punycode |
|---|---|
| नेपाल.नेपाल | xn--n2bm2a.xn--n2bm2a |
| क्यान.संगठन | xn--11b2bu4dwd.xn--i1b6b1a6a2e |
| مثال.إختبار | xn--mgbh0fb.xn--kgbechtv |
| 例子.广告 | xn--fsq270a.xn--fiqs8s |

---

# 🇳🇵 Nepal Relevance

Nepal officially supports the `.नेपाल` ccTLD, but many systems still reject Nepali email addresses.

UAReady enables:

- Nepali-language digital identity
- Unicode email validation
- Government onboarding systems
- Native-script domain verification
- SMTPUTF8-ready infrastructure

This directly supports Nepal’s movement toward localized internet services and inclusive digital access.

---

# 📡 Live SMTPUTF8 Test Server

```text
Email: test8@क्यान.संगठन
Username: mailbox10
Password: test8
```

SMTPUTF8-compatible mail server:

```text
mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e
```

---

# 🛰️ SMTPUTF8 Capability Check

```python
import smtplib

with smtplib.SMTP('mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e') as s:
    features = s.esmtp_features
    print('SMTPUTF8 supported:', 'smtputf8' in features)
```

---

# 📈 Stretch Goals

- ⭐ Browser-based live validator
- ⭐ MX record lookup
- ⭐ Real SMTP send testing
- ⭐ Multi-script rendering validation
- ⭐ Docker deployment
- ⭐ Public validation API

---

# ⚠️ Known Limitations

- Bidi (RTL/LTR) rendering validation not implemented
- SMTP live delivery requires internet access
- Full mailbox existence verification not included
- Advanced Unicode spoof detection not implemented

---

# 🤝 Contributors

| Profile | Name |
|---|---|
| <img src="https://github.com/nushhkaa.png" width="80"> | [Anushka Bashyal](https://github.com/nushhkaa) |
| <img src="https://github.com/Indoorfinality.png" width="80"> | [Anushna Chaugain](https://github.com/Indoorfinality) |
| <img src="https://github.com/Coderkabish.png" width="80"> | [Kavish Dahal](https://github.com/Coderkabish) |
| <img src="https://github.com/DS-kj.png" width="80"> | [Kunjang Sherpa](https://github.com/DS-kj) |
| <img src="https://github.com/rishicares.png" width="80"> | [Rishikesh Gautam](https://github.com/rishicares) |
| <img src="https://github.com/bgprogrammer909.png" width="80"> | [Suchit Ratna Bajracharya](https://github.com/bgprogrammer909) |

---

# 🏆 Evaluation Focus

| Category | Weight |
|---|---|
| Standards Compliance | 30% |
| Technical Execution | 25% |
| Script Coverage | 20% |
| Nepal Relevance | 15% |
| Presentation | 10% |

---

# 🛠️ Technologies Used

- Python
- Flask
- idna
- dnspython
- Unicode NFC
- SMTPUTF8
- IDNA2008

---

# 🤝 Contributing

Contributions are welcome.

Ideas:
- Add more scripts
- Improve spoof detection
- Add GUI dashboard
- Improve DNS validation
- Add Docker support

---

# 📜 License

MIT License

---

# ❤️ Final Note

> “Language should never be a barrier to digital identity.”

UAReady helps make the internet more inclusive by enabling email validation in every language — starting with Nepal.
