"""Admin API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import jwt
from src.config import settings
from src.db.connection import get_db
from src.models.provider import Provider
from src.models.booking import Booking
from src.models.conversation import Conversation
from src.models.message import Message
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin_token(token: str = None) -> bool:
    """Verify admin JWT token."""
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(
            token,
            settings.admin_jwt_secret,
            algorithms=[settings.admin_jwt_algorithm],
        )
        return True
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/providers/{provider_id}/approve")
async def approve_provider(
    provider_id: int,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Approve a provider (set verification_status to 'approved')."""
    verify_admin_token(token)

    provider = db.query(Provider).filter_by(id=provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider.verification_status = "approved"
    db.commit()

    logger.info(f"Provider {provider_id} approved by admin")
    return {
        "success": True,
        "provider_id": provider_id,
        "status": "approved"
    }


@router.post("/providers/{provider_id}/reject")
async def reject_provider(
    provider_id: int,
    reason: str = None,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Reject a provider."""
    verify_admin_token(token)

    provider = db.query(Provider).filter_by(id=provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider.verification_status = "rejected"
    db.commit()

    logger.info(f"Provider {provider_id} rejected by admin. Reason: {reason}")
    return {
        "success": True,
        "provider_id": provider_id,
        "status": "rejected",
        "reason": reason,
    }


@router.get("/bookings")
async def list_bookings(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    token: str = None,
    db: Session = Depends(get_db),
):
    """List bookings with optional status filter."""
    verify_admin_token(token)

    query = db.query(Booking)
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    bookings = query.order_by(Booking.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "bookings": [
            {
                "id": b.id,
                "patient_wa_id": b.patient_wa_id,
                "provider_id": b.provider_id,
                "status": b.status,
                "scheduled_at": b.scheduled_at,
                "created_at": b.created_at.isoformat(),
            }
            for b in bookings
        ]
    }


@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: int,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Get booking details."""
    verify_admin_token(token)

    booking = db.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {
        "id": booking.id,
        "patient_wa_id": booking.patient_wa_id,
        "provider_id": booking.provider_id,
        "service_id": booking.service_id,
        "status": booking.status,
        "symptoms": booking.symptoms,
        "address": booking.address,
        "pin": booking.pin,
        "scheduled_at": booking.scheduled_at,
        "created_at": booking.created_at.isoformat(),
    }


@router.post("/bookings/{booking_id}/update-status")
async def update_booking_status(
    booking_id: int,
    new_status: str,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Update booking status."""
    verify_admin_token(token)

    booking = db.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    valid_statuses = ["requested", "provider_assigned", "accepted", "en_route", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    booking.status = new_status
    if new_status == "completed":
        booking.completed_at = datetime.now()
    db.commit()

    logger.info(f"Booking {booking_id} status updated to {new_status}")
    return {"success": True, "booking_id": booking_id, "status": new_status}


@router.get("/conversations/{wa_id}")
async def get_conversation(
    wa_id: str,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Get conversation details and message history."""
    verify_admin_token(token)

    conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter_by(wa_id=wa_id).order_by(Message.created_at).all()

    return {
        "wa_id": wa_id,
        "state": conversation.state,
        "language": conversation.language,
        "is_escalated": conversation.is_escalated,
        "escalated_at": conversation.escalated_to_human_at.isoformat() if conversation.escalated_to_human_at else None,
        "turn_count": conversation.turn_count,
        "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None,
        "messages": [
            {
                "id": m.id,
                "direction": m.direction,
                "type": m.message_type,
                "body": m.body,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]
    }


@router.post("/conversations/{wa_id}/takeover")
async def takeover_conversation(
    wa_id: str,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Admin takes over a conversation (escalates and stops auto-replies)."""
    verify_admin_token(token)

    conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.is_escalated = True
    conversation.escalated_to_human_at = datetime.now()
    db.commit()

    logger.info(f"Admin took over conversation {wa_id}")
    return {
        "success": True,
        "wa_id": wa_id,
        "message": "Conversation escalated. Auto-replies stopped."
    }


@router.post("/conversations/{wa_id}/resume")
async def resume_conversation(
    wa_id: str,
    token: str = None,
    db: Session = Depends(get_db),
):
    """Resume automated replies for a conversation."""
    verify_admin_token(token)

    conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.is_escalated = False
    db.commit()

    logger.info(f"Resumed conversation {wa_id}")
    return {
        "success": True,
        "wa_id": wa_id,
        "message": "Conversation resumed. Auto-replies enabled."
    }
