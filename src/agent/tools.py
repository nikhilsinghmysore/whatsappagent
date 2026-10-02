"""Tool implementations for the Claude agent."""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.patient import Patient
from src.models.provider import Provider
from src.models.booking import Booking
from src.models.service import Service
from typing import List, Dict, Any


def search_providers(
    db: Session,
    service_category: str,
    pin_code: str,
    scheduled_date: str,
) -> str:
    """
    Search for available providers by service category, location, and date.
    Returns JSON with provider options or error message.
    """
    try:
        # Find service
        service = db.query(Service).filter_by(category=service_category).first()
        if not service:
            return json.dumps({"error": f"Service '{service_category}' not found"})

        # Search providers: approved, matching service, in service area, online
        providers = db.query(Provider).filter(
            Provider.category == service_category,
            Provider.verification_status == "approved",
            Provider.is_online == True,
        ).all()

        # Filter by service area (pin code)
        matching_providers = []
        for provider in providers:
            if provider.service_area and pin_code in provider.service_area:
                matching_providers.append(provider)

        if not matching_providers:
            return json.dumps({"error": "No providers available in your area"})

        # Format response
        providers_list = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "fee": float(p.fee) if p.fee else 0,
                "rating": float(p.rating_avg) if p.rating_avg else 0,
                "total_bookings": p.total_bookings,
            }
            for p in matching_providers[:3]  # Top 3 providers
        ]

        return json.dumps({
            "success": True,
            "count": len(providers_list),
            "providers": providers_list
        })

    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})


def create_booking(
    db: Session,
    patient_wa_id: str,
    service_category: str,
    provider_id: int,
    symptoms: str,
    address: str,
    pin_code: str,
    scheduled_date: str,
    scheduled_time: str,
) -> str:
    """
    Create a new booking.
    Returns booking ID and confirmation details.
    """
    try:
        # Verify patient exists or create
        patient = db.query(Patient).filter_by(wa_id=patient_wa_id).first()
        if not patient:
            return json.dumps({"error": "Patient not found. Please complete registration first."})

        # Verify service
        service = db.query(Service).filter_by(category=service_category).first()
        if not service:
            return json.dumps({"error": f"Service '{service_category}' not found"})

        # Verify provider
        provider = db.query(Provider).filter_by(id=provider_id).first()
        if not provider or provider.verification_status != "approved":
            return json.dumps({"error": "Provider not available"})

        # Create booking
        booking = Booking(
            patient_wa_id=patient_wa_id,
            provider_id=provider_id,
            service_id=service.id,
            status="requested",
            symptoms=symptoms,
            address=address,
            pin=pin_code,
            scheduled_at=f"{scheduled_date}T{scheduled_time}",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return json.dumps({
            "success": True,
            "booking_id": booking.id,
            "status": "requested",
            "provider_name": provider.name,
            "provider_fee": float(provider.fee) if provider.fee else 0,
            "scheduled_at": booking.scheduled_at,
            "message": "Booking created! Provider will respond shortly."
        })

    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Booking creation failed: {str(e)}"})


def get_booking(db: Session, booking_id: int) -> str:
    """Get booking details and status."""
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            return json.dumps({"error": f"Booking {booking_id} not found"})

        provider = db.query(Provider).filter_by(id=booking.provider_id).first()
        service = db.query(Service).filter_by(id=booking.service_id).first()

        return json.dumps({
            "success": True,
            "booking_id": booking.id,
            "status": booking.status,
            "service": service.name if service else "Unknown",
            "provider": provider.name if provider else "Unassigned",
            "scheduled_at": booking.scheduled_at,
            "address": booking.address,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
        })

    except Exception as e:
        return json.dumps({"error": f"Get booking failed: {str(e)}"})


def cancel_booking(db: Session, booking_id: int) -> str:
    """Cancel an existing booking."""
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            return json.dumps({"error": f"Booking {booking_id} not found"})

        if booking.status in ["completed", "cancelled"]:
            return json.dumps({"error": f"Cannot cancel booking with status {booking.status}"})

        booking.status = "cancelled"
        db.commit()

        return json.dumps({
            "success": True,
            "booking_id": booking.id,
            "status": "cancelled",
            "message": "Booking cancelled successfully"
        })

    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Cancellation failed: {str(e)}"})


def reschedule_booking(
    db: Session,
    booking_id: int,
    new_date: str,
    new_time: str,
) -> str:
    """Reschedule a booking to a new date/time."""
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            return json.dumps({"error": f"Booking {booking_id} not found"})

        if booking.status not in ["requested", "provider_assigned"]:
            return json.dumps({"error": f"Cannot reschedule booking with status {booking.status}"})

        booking.scheduled_at = f"{new_date}T{new_time}"
        booking.status = "requested"  # Reset to requested
        db.commit()

        return json.dumps({
            "success": True,
            "booking_id": booking.id,
            "new_scheduled_at": booking.scheduled_at,
            "message": "Booking rescheduled successfully"
        })

    except Exception as e:
        db.rollback()
        return json.dumps({"error": f"Reschedule failed: {str(e)}"})


def escalate_to_human(db: Session, wa_id: str, reason: str) -> str:
    """Escalate conversation to human admin."""
    try:
        from src.models.conversation import Conversation

        conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()
        if conversation:
            conversation.is_escalated = True
            conversation.escalated_to_human_at = datetime.now()
            db.commit()

        return json.dumps({
            "success": True,
            "message": f"Chat escalated to human admin. Reason: {reason}",
            "admin_notification": f"Escalation from {wa_id}: {reason}"
        })

    except Exception as e:
        return json.dumps({"error": f"Escalation failed: {str(e)}"})
