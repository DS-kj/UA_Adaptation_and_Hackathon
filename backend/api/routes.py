import asyncio
import smtplib
import ssl
from email.headerregistry import Address
from email.message import EmailMessage

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from validator import validate_domain_name, validate_email_address

from .models import (
    BatchRequest,
    ContactRequest,
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


def _send_contact_email(to_addr: str) -> None:
    import os
    smtp_host = os.environ.get("SMTP_HOST", "mail.xn--11b2bu4dwd.xn--i1b6b1a6a2e")
    smtp_port = int(os.environ.get("SMTP_PORT", "25"))
    smtp_user = os.environ.get("SMTP_USER", "mailbox10")
    smtp_pass = os.environ.get("SMTP_PASS", "test8")
    from_addr = os.environ.get("SMTP_FROM", "test8@क्यान.संगठन")

    msg = EmailMessage()
    msg["Subject"] = "Thank you for contacting CAN InfoTech"
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg.set_content(
        f"Dear User,\n\n"
        f"Thank you for reaching out to CAN InfoTech.\n"
        f"We have received your message at {to_addr} and will get back to you shortly.\n\n"
        f"Best regards,\n"
        f"CAN InfoTech Team\n"
        f"Computer Association of Nepal"
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            if smtp.has_extn("STARTTLS"):
                smtp.starttls(ssl.create_default_context())
                smtp.ehlo()
            if smtp_user:
                smtp.login(smtp_user, smtp_pass)
            mail_options = ["SMTPUTF8"] if smtp.has_extn("SMTPUTF8") else []
            smtp.sendmail(from_addr, [to_addr], msg.as_bytes(), mail_options=mail_options)
    except Exception:
        pass  # best-effort — errors are silently dropped


@router.post("/contact", summary="Contact Us — validate email and send confirmation")
async def api_contact(req: ContactRequest, background_tasks: BackgroundTasks) -> dict:
    result = validate_email_address(req.email)
    if not result["valid"]:
        return {"success": False, "error": result["error"]}

    background_tasks.add_task(_send_contact_email, req.email)
    return {"success": True, "to": req.email}


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "UAReady Validator", "version": "1.0.0"}
