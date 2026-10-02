"""Background tasks for ARQ worker."""

import logging
from datetime import datetime, timedelta
from src.db.connection import SessionLocal
from src.whatsapp.client import WhatsAppClient
from src.whatsapp.templates import (
    send_booking_confirmation,
    send_visit_reminder,
    send_provider_request,
    send_provider_on_the_way,
    send_feedback_request,
)
from src.services.booking_service import get_upcoming_bookings, get_bookings_for_provider
from src.models.provider import Provider
from src.models.booking import Booking

logger = logging.getLogger(__name__)
whatsapp_client = WhatsAppClient()


async def send_booking_confirmation_reminder(booking_id: int):
    """Send booking confirmation to patient and provider."""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            logger.warning(f"Booking {booking_id} not found")
            return

        provider = db.query(Provider).filter_by(id=booking.provider_id).first()
        service = db.query(Booking).filter_by(id=booking_id).first()

        # Send to patient
        await send_booking_confirmation(
            booking.patient_wa_id,
            provider.name if provider else "Assigned",
            "Your Service",
            booking.scheduled_at,
            provider.fee if provider else 0,
            booking_id,
        )

        # Send to provider
        if provider:
            await send_provider_request(
                provider.wa_id,
                "Patient",
                "Your Service",
                booking.scheduled_at,
                booking.address,
                booking_id,
            )

        logger.info(f"Sent confirmation for booking {booking_id}")
    except Exception as e:
        logger.error(f"Error sending confirmation for booking {booking_id}: {e}")
    finally:
        db.close()


async def send_visit_reminders():
    """Send reminders for appointments 24 hours before."""
    db = SessionLocal()
    try:
        # Get bookings scheduled in 23-25 hours
        now = datetime.now()
        in_24_hours = now + timedelta(hours=24)
        in_23_hours = now + timedelta(hours=23)

        bookings = get_upcoming_bookings(db, hours_ahead=25)
        bookings = [b for b in bookings if in_23_hours < b.scheduled_at < in_24_hours]

        for booking in bookings:
            provider = db.query(Provider).filter_by(id=booking.provider_id).first()

            await send_visit_reminder(
                booking.patient_wa_id,
                provider.name if provider else "Your Provider",
                booking.scheduled_at,
                booking.id,
            )

        logger.info(f"Sent {len(bookings)} visit reminders")
    except Exception as e:
        logger.error(f"Error sending visit reminders: {e}")
    finally:
        db.close()


async def send_feedback_reminders():
    """Send feedback requests for completed bookings."""
    db = SessionLocal()
    try:
        from sqlalchemy import func, and_

        # Get bookings completed in the last 24 hours without ratings
        from src.models.rating import Rating

        now = datetime.now()
        yesterday = now - timedelta(hours=24)

        completed_bookings = db.query(Booking).filter(
            Booking.status == "completed",
            Booking.completed_at.between(yesterday, now),
        ).all()

        for booking in completed_bookings:
            # Check if already rated
            existing_rating = db.query(Rating).filter_by(booking_id=booking.id).first()
            if existing_rating:
                continue

            provider = db.query(Provider).filter_by(id=booking.provider_id).first()

            await send_feedback_request(
                booking.patient_wa_id,
                provider.name if provider else "Your Provider",
                booking.id,
            )

        logger.info(f"Sent {len(completed_bookings)} feedback requests")
    except Exception as e:
        logger.error(f"Error sending feedback requests: {e}")
    finally:
        db.close()


async def cleanup_stale_conversations():
    """Clean up old conversation state (remove archived conversations)."""
    db = SessionLocal()
    try:
        from src.models.conversation import Conversation

        # Mark conversations as completed if no messages in 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)

        stale = db.query(Conversation).filter(
            Conversation.last_message_at < seven_days_ago,
            Conversation.state != "completed",
        ).all()

        for conv in stale:
            conv.state = "completed"

        db.commit()
        logger.info(f"Marked {len(stale)} conversations as completed")
    except Exception as e:
        logger.error(f"Error cleaning up conversations: {e}")
    finally:
        db.close()


async def handle_provider_timeout(booking_id: int):
    """
    Handle provider request timeout (5 minutes).
    If provider hasn't responded, try next provider or cancel.
    """
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        if not booking or booking.status != "provider_assigned":
            return

        # Mark as timed out, assign to next provider or cancel
        booking.status = "requested"  # Back to requesting state
        db.commit()
        logger.info(f"Provider timeout for booking {booking_id}")
    except Exception as e:
        logger.error(f"Error handling provider timeout: {e}")
    finally:
        db.close()
