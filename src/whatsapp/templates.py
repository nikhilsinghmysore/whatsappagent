"""WhatsApp message templates and template management."""

from datetime import datetime
from sqlalchemy.orm import Session
from src.whatsapp.client import WhatsAppClient
from src.models.consent import Consent
import logging

logger = logging.getLogger(__name__)

whatsapp_client = WhatsAppClient()

TEMPLATES = {
    "booking_confirmation": {
        "name": "booking_confirmation",
        "language": "en",
        "description": "Booking confirmation with provider details",
    },
    "visit_reminder": {
        "name": "visit_reminder",
        "language": "en",
        "description": "Reminder 24 hours before visit",
    },
    "provider_new_request": {
        "name": "provider_new_request",
        "language": "en",
        "description": "New booking request for provider",
    },
    "provider_on_the_way": {
        "name": "provider_on_the_way",
        "language": "en",
        "description": "Provider is on the way notification",
    },
    "feedback_request": {
        "name": "feedback_request",
        "language": "en",
        "description": "Request feedback after service",
    },
}


async def check_template_consent(db: Session, wa_id: str, template_name: str) -> bool:
    """Check if user has opted in to a template."""
    consent = db.query(Consent).filter_by(
        wa_id=wa_id,
        template_name=template_name,
        opted_in=True,
    ).first()
    return consent is not None


async def record_template_consent(
    db: Session,
    wa_id: str,
    template_name: str,
    opted_in: bool = True,
):
    """Record user's consent for a template."""
    consent = Consent(
        wa_id=wa_id,
        template_name=template_name,
        opted_in=opted_in,
        timestamp=datetime.now(),
    )
    db.add(consent)
    db.commit()


async def send_booking_confirmation(
    wa_id: str,
    provider_name: str,
    service_name: str,
    scheduled_time: str,
    fee: float,
    booking_id: int,
):
    """Send booking confirmation template."""
    try:
        message = f"""✅ Booking Confirmed!

Provider: {provider_name}
Service: {service_name}
Scheduled: {scheduled_time}
Fee: ₹{fee:.0f}
Booking ID: {booking_id}

You will receive updates about the provider's arrival. Contact us for any changes."""

        await whatsapp_client.send_text_message(wa_id, message)
        logger.info(f"Sent booking confirmation to {wa_id}")
    except Exception as e:
        logger.error(f"Error sending booking confirmation: {e}")


async def send_visit_reminder(
    wa_id: str,
    provider_name: str,
    scheduled_time: str,
    booking_id: int,
):
    """Send visit reminder 24 hours before."""
    try:
        message = f"""📅 Appointment Reminder

Your appointment with {provider_name} is scheduled for {scheduled_time}.

Please ensure someone is available at home. Contact us if you need to reschedule.
Booking ID: {booking_id}"""

        await whatsapp_client.send_text_message(wa_id, message)
        logger.info(f"Sent visit reminder to {wa_id}")
    except Exception as e:
        logger.error(f"Error sending visit reminder: {e}")


async def send_provider_request(
    provider_wa_id: str,
    patient_name: str,
    service_name: str,
    scheduled_time: str,
    address: str,
    booking_id: int,
):
    """Send booking request to provider."""
    try:
        message = f"""🔔 New Booking Request

Patient: {patient_name}
Service: {service_name}
Time: {scheduled_time}
Address: {address}
Booking ID: {booking_id}

Please respond within 5 minutes. You can Accept or Reject this booking."""

        await whatsapp_client.send_text_message(provider_wa_id, message)
        logger.info(f"Sent booking request to provider {provider_wa_id}")
    except Exception as e:
        logger.error(f"Error sending provider request: {e}")


async def send_provider_on_the_way(
    wa_id: str,
    provider_name: str,
    provider_contact: str,
):
    """Notify patient that provider is on the way."""
    try:
        message = f"""🚗 Your Service Provider is On the Way!

Provider: {provider_name}
Contact: {provider_contact}

Please ensure someone is home to receive them."""

        await whatsapp_client.send_text_message(wa_id, message)
        logger.info(f"Sent on-the-way notification to {wa_id}")
    except Exception as e:
        logger.error(f"Error sending on-the-way notification: {e}")


async def send_feedback_request(
    wa_id: str,
    provider_name: str,
    booking_id: int,
):
    """Request feedback after service completion."""
    try:
        message = f"""⭐ How was your experience?

Please rate your appointment with {provider_name} and help us improve.

Reply with a rating from 1-5 stars (1=Poor, 5=Excellent)
Booking ID: {booking_id}"""

        await whatsapp_client.send_text_message(wa_id, message)
        logger.info(f"Sent feedback request to {wa_id}")
    except Exception as e:
        logger.error(f"Error sending feedback request: {e}")
