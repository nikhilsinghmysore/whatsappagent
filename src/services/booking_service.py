"""Booking management service."""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.booking import Booking
from src.models.rating import Rating

logger = logging.getLogger(__name__)


def create_booking(
    db: Session,
    patient_wa_id: str,
    service_id: int,
    provider_id: int,
    symptoms: str,
    address: str,
    pin: str,
    scheduled_at: str,
) -> Booking:
    """Create a new booking."""
    booking = Booking(
        patient_wa_id=patient_wa_id,
        provider_id=provider_id,
        service_id=service_id,
        status="requested",
        symptoms=symptoms,
        address=address,
        pin=pin,
        scheduled_at=scheduled_at,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    logger.info(f"Created booking {booking.id} for patient {patient_wa_id}")
    return booking


def update_booking_status(
    db: Session,
    booking_id: int,
    new_status: str,
) -> Booking:
    """Update booking status with state validation."""
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        return None

    valid_states = ["requested", "provider_assigned", "accepted", "en_route", "completed", "cancelled"]
    if new_status not in valid_states:
        logger.warning(f"Invalid status {new_status} for booking {booking_id}")
        return None

    booking.status = new_status
    if new_status == "completed":
        booking.completed_at = datetime.now()
    elif new_status == "accepted":
        booking.provider_response_at = datetime.now()

    db.commit()
    db.refresh(booking)
    logger.info(f"Booking {booking_id} status updated to {new_status}")
    return booking


def assign_provider(
    db: Session,
    booking_id: int,
    provider_id: int,
) -> Booking:
    """Assign a provider to a booking."""
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if booking:
        booking.provider_id = provider_id
        booking.status = "provider_assigned"
        db.commit()
        db.refresh(booking)
        logger.info(f"Assigned provider {provider_id} to booking {booking_id}")
    return booking


def cancel_booking(db: Session, booking_id: int) -> Booking:
    """Cancel a booking."""
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if booking and booking.status not in ["completed", "cancelled"]:
        booking.status = "cancelled"
        db.commit()
        db.refresh(booking)
        logger.info(f"Cancelled booking {booking_id}")
    return booking


def reschedule_booking(
    db: Session,
    booking_id: int,
    new_scheduled_at: str,
) -> Booking:
    """Reschedule a booking."""
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if booking and booking.status in ["requested", "provider_assigned"]:
        booking.scheduled_at = new_scheduled_at
        booking.status = "requested"  # Reset to requested after reschedule
        db.commit()
        db.refresh(booking)
        logger.info(f"Rescheduled booking {booking_id} to {new_scheduled_at}")
    return booking


def get_bookings_for_provider(db: Session, provider_id: int, status: str = None) -> list:
    """Get bookings for a provider, optionally filtered by status."""
    query = db.query(Booking).filter_by(provider_id=provider_id)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Booking.scheduled_at).all()


def get_upcoming_bookings(db: Session, hours_ahead: int = 24) -> list:
    """Get bookings scheduled in the next N hours."""
    now = datetime.now()
    future = now + timedelta(hours=hours_ahead)

    bookings = db.query(Booking).filter(
        Booking.scheduled_at.between(now, future),
        Booking.status.in_(["requested", "provider_assigned", "accepted", "en_route"]),
    ).all()
    return bookings


def add_booking_rating(
    db: Session,
    booking_id: int,
    patient_wa_id: str,
    provider_id: int,
    rating: int,
    feedback: str = None,
) -> Rating:
    """Add a rating to a completed booking."""
    rating_record = Rating(
        booking_id=booking_id,
        patient_wa_id=patient_wa_id,
        provider_id=provider_id,
        rating=rating,
        feedback_text=feedback,
    )
    db.add(rating_record)
    db.commit()
    db.refresh(rating_record)
    logger.info(f"Added rating {rating} for booking {booking_id}")
    return rating_record
