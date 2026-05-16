from pydantic import BaseModel, Field
from typing import Literal


class EmailRequest(BaseModel):
    email: str = Field(..., examples=["राम@नेपाल.नेपाल"])
    lang: Literal["en", "ne", "ar"] = Field("en", description="Language for error messages")


class DomainRequest(BaseModel):
    domain: str = Field(..., examples=["नेपाल.नेपाल"])
    lang: Literal["en", "ne", "ar"] = Field("en")


class BatchItem(BaseModel):
    type: Literal["email", "domain"]
    value: str


class BatchRequest(BaseModel):
    items: list[BatchItem] = Field(..., max_length=50)
    lang: Literal["en", "ne", "ar"] = Field("en")


class ContactRequest(BaseModel):
    email: str = Field(..., examples=["user@example.com"])


class SmtpCapabilityRequest(BaseModel):
    host: str = Field(..., examples=["smtp.gmail.com"])
    port: int = Field(587, ge=1, le=65535)
    timeout: float = Field(10.0, ge=1.0, le=30.0, description="Connection timeout in seconds")


class SmtpSendRequest(BaseModel):
    host: str
    port: int = Field(587, ge=1, le=65535)
    username: str
    password: str
    from_addr: str = Field(..., examples=["राम@नेपाल.नेपाल"])
    to_addr: str = Field(..., examples=["test@example.com"])
    subject: str = Field("UAReady SMTPUTF8 Test — नेपाल २०२६")
    body: str = Field("This is a test message sent using SMTPUTF8 (RFC 6531).\n\nइमेल परीक्षण सफल भयो।")
    use_tls: bool = True
