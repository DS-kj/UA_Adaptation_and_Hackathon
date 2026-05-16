import asyncio
import smtplib
import ssl
from email.headerregistry import Address
from email.message import EmailMessage

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from validator import validate_domain_name, validate_email_address

from .models import (
    BatchRequest,
    DomainRequest,
    EmailRequest,
    SmtpCapabilityRequest,
    SmtpSendRequest,
)

router = APIRouter()


@router.post("/validate/email", summary="Validate an internationalised email address")
async def api_validate_email(req: EmailRequest) -> dict:
    return validate_email_address(req.email, req.lang)


@router.post("/validate/domain", summary="Validate an internationalised domain name")
async def api_validate_domain(req: DomainRequest) -> dict:
    return validate_domain_name(req.domain, req.lang)


@router.post("/validate/batch", summary="Validate multiple emails and/or domains at once")
async def api_validate_batch(req: BatchRequest) -> dict:
    results = []
    for item in req.items:
        if item.type == "email":
            result = validate_email_address(item.value, req.lang)
        else:
            result = validate_domain_name(item.value, req.lang)
        results.append({"type": item.type, "value": item.value, **result})
    return {
        "count": len(results),
        "valid_count": sum(1 for r in results if r["valid"]),
        "results": results,
    }


@router.post("/smtp/capability", summary="Check if an SMTP server supports SMTPUTF8")
async def api_smtp_capability(req: SmtpCapabilityRequest) -> dict:
    """
    Connect to an SMTP server, issue EHLO, and report which extensions it advertises.
    This tests RFC 6531 (SMTPUTF8) server-side support without sending any mail.
    """
    def _check() -> dict:
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(req.host, req.port, timeout=req.timeout) as smtp:
                smtp.ehlo()
                # Attempt STARTTLS if available
                if smtp.has_extn("STARTTLS"):
                    smtp.starttls(context=context)
                    smtp.ehlo()

                extensions = list(smtp.esmtp_features.keys())
                supports_smtputf8 = smtp.has_extn("SMTPUTF8")
                supports_8bitmime = smtp.has_extn("8BITMIME")

                return {
                    "reachable": True,
                    "host": req.host,
                    "port": req.port,
                    "supports_smtputf8": supports_smtputf8,
                    "supports_8bitmime": supports_8bitmime,
                    "extensions": sorted(extensions),
                    "ua_ready": supports_smtputf8,
                }
        except Exception as exc:
            return {"reachable": False, "host": req.host, "port": req.port, "error": str(exc)}

    result = await asyncio.get_event_loop().run_in_executor(None, _check)
    return result


@router.post("/smtp/send-test", summary="Send a test email using SMTPUTF8")
async def api_smtp_send(req: SmtpSendRequest) -> dict:
    """
    Send a test email using SMTPUTF8 to demonstrate end-to-end RFC 6531 compliance.
    Requires credentials for an SMTPUTF8-capable outbound SMTP server.
    """
    # Validate both addresses first
    from_result = validate_email_address(req.from_addr)
    to_result = validate_email_address(req.to_addr)

    if not from_result["valid"]:
        return {"sent": False, "error": f"Invalid from address: {from_result['error']}"}
    if not to_result["valid"]:
        return {"sent": False, "error": f"Invalid to address: {to_result['error']}"}

    def _send() -> dict:
        msg = EmailMessage()
        msg["Subject"] = req.subject
        msg["From"] = req.from_addr
        msg["To"] = req.to_addr
        msg.set_content(req.body)
        # Mark as UTF-8 body per RFC 6532
        msg.set_charset("utf-8")

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(req.host, req.port, timeout=15) as smtp:
                smtp.ehlo()
                if req.use_tls and smtp.has_extn("STARTTLS"):
                    smtp.starttls(context=context)
                    smtp.ehlo()

                if not smtp.has_extn("SMTPUTF8"):
                    return {
                        "sent": False,
                        "error": f"Server {req.host}:{req.port} does not advertise SMTPUTF8 — cannot send internationalised addresses",
                    }

                smtp.login(req.username, req.password)
                # mail_options=["SMTPUTF8"] is the key RFC 6531 addition
                smtp.sendmail(
                    req.from_addr,
                    [req.to_addr],
                    msg.as_bytes(),
                    mail_options=["SMTPUTF8"],
                )
                return {
                    "sent": True,
                    "from": req.from_addr,
                    "to": req.to_addr,
                    "smtputf8_used": True,
                    "standards": ["RFC 6531 (SMTPUTF8)", "RFC 6532 (EAI)"],
                }
        except smtplib.SMTPAuthenticationError:
            return {"sent": False, "error": "SMTP authentication failed — check username/password"}
        except smtplib.SMTPException as exc:
            return {"sent": False, "error": f"SMTP error: {exc}"}
        except Exception as exc:
            return {"sent": False, "error": str(exc)}

    result = await asyncio.get_event_loop().run_in_executor(None, _send)
    return result


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "UAReady Validator", "version": "1.0.0"}
