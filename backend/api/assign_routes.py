import logging
import os

import httpx

from fastapi import APIRouter, Depends, HTTPException

from api.deps import require_admin
from api.schemas import AssignRequest
from security.audit import log_security_event

router = APIRouter()
logger = logging.getLogger("insider_threat_api.email")
BREVO_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"


class EmailDeliveryError(RuntimeError):
    pass


def send_email(employee: str, note: str) -> None:
    api_key = os.getenv("BREVO_API_KEY")
    sender = os.getenv("MAIL_FROM_EMAIL") or os.getenv("ADMIN_EMAIL")
    sender_name = os.getenv("MAIL_FROM_NAME", "InsiderSentinel").strip() or "InsiderSentinel"
    recipient = os.getenv("ANALYST_EMAIL")
    if not all((api_key, sender, recipient)):
        logger.warning("Email notification is not configured")
        raise EmailDeliveryError("Email notification is not configured")

    payload = {
        "sender": {"name": sender_name, "email": sender},
        "to": [{"email": recipient}],
        "subject": f"Employee {employee} Assigned for Review",
        "textContent": f"Employee: {employee}\n\nAdmin Note:\n{note}\n",
    }

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(
                BREVO_EMAIL_URL,
                headers={
                    "accept": "application/json",
                    "api-key": api_key,
                    "content-type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        error_code = "unknown"
        try:
            error_code = exc.response.json().get("code", "unknown")
        except ValueError:
            pass
        logger.error(
            "Brevo rejected the email notification: status=%s code=%s",
            exc.response.status_code,
            error_code,
        )
        raise EmailDeliveryError("Brevo rejected the email notification") from exc
    except httpx.RequestError as exc:
        logger.error("Brevo email request failed: %s", type(exc).__name__)
        raise EmailDeliveryError("Could not connect to Brevo") from exc


@router.post("/assign")
def assign_to_analyst(req: AssignRequest, user=Depends(require_admin)):
    try:
        send_email(req.employee, req.note)
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Email could not be sent. Check the Brevo API key and verify "
                "the configured sender email as a Brevo sender."
            ),
        ) from exc

    log_security_event("employee_assigned", user["sub"], req.employee)
    return {"message": "Email sent to analyst"}
