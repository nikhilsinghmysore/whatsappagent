"""Privacy and data deletion endpoints (DPDP Act compliance)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.connection import get_db
from src.models.patient import Patient
from src.models.message import Message
from src.models.conversation import Conversation
from src.models.booking import Booking
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.post("/delete-patient-data")
async def delete_patient_data(
    wa_id: str,
    confirmation: bool = False,
    db: Session = Depends(get_db),
):
    """
    Delete all patient data (DPDP Act compliance).
    Requires explicit confirmation.
    """
    if not confirmation:
        return {
            "error": "Deletion requires explicit confirmation. Set confirmation=true"
        }

    try:
        patient = db.query(Patient).filter_by(wa_id=wa_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Delete in order: messages, bookings, ratings, conversations, patient
        message_count = db.query(Message).filter_by(wa_id=wa_id).delete()

        booking_ids = [b.id for b in db.query(Booking).filter_by(patient_wa_id=wa_id).all()]
        from src.models.rating import Rating
        db.query(Rating).filter(Rating.booking_id.in_(booking_ids)).delete()

        booking_count = db.query(Booking).filter_by(patient_wa_id=wa_id).delete()

        from src.models.consent import Consent
        db.query(Consent).filter_by(wa_id=wa_id).delete()

        conversation_count = db.query(Conversation).filter_by(wa_id=wa_id).delete()

        patient_count = db.query(Patient).filter_by(wa_id=wa_id).delete()

        db.commit()

        logger.info(
            f"Deleted patient data for {wa_id}: "
            f"{patient_count} patients, {booking_count} bookings, "
            f"{message_count} messages, {conversation_count} conversations"
        )

        return {
            "success": True,
            "message": "All patient data has been deleted",
            "deleted": {
                "patients": patient_count,
                "bookings": booking_count,
                "messages": message_count,
                "conversations": conversation_count,
            }
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting patient data for {wa_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-export/{wa_id}")
async def export_patient_data(
    wa_id: str,
    db: Session = Depends(get_db),
):
    """
    Export all patient data in JSON format (for data portability).
    """
    try:
        patient = db.query(Patient).filter_by(wa_id=wa_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        messages = db.query(Message).filter_by(wa_id=wa_id).all()
        bookings = db.query(Booking).filter_by(patient_wa_id=wa_id).all()
        conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()
        from src.models.consent import Consent
        consents = db.query(Consent).filter_by(wa_id=wa_id).all()

        return {
            "export_timestamp": datetime.now().isoformat(),
            "patient": {
                "wa_id": patient.wa_id,
                "name": patient.name,
                "age": patient.age,
                "language": patient.language,
                "default_address": patient.default_address,
                "pin": patient.pin,
                "created_at": patient.created_at.isoformat() if patient.created_at else None,
            },
            "conversation": {
                "state": conversation.state if conversation else None,
                "language": conversation.language if conversation else None,
                "turn_count": conversation.turn_count if conversation else 0,
                "last_message_at": conversation.last_message_at.isoformat() if conversation and conversation.last_message_at else None,
            } if conversation else None,
            "messages": [
                {
                    "id": m.id,
                    "direction": m.direction,
                    "type": m.message_type,
                    "body": m.body,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
            "bookings": [
                {
                    "id": b.id,
                    "status": b.status,
                    "symptoms": b.symptoms,
                    "address": b.address,
                    "scheduled_at": b.scheduled_at,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                }
                for b in bookings
            ],
            "consents": [
                {
                    "template_name": c.template_name,
                    "opted_in": c.opted_in,
                    "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                }
                for c in consents
            ],
        }

    except Exception as e:
        logger.error(f"Error exporting data for {wa_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
