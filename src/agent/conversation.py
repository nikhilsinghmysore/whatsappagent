"""Conversation state management."""

import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.patient import Patient

logger = logging.getLogger(__name__)


def get_or_create_conversation(db: Session, wa_id: str) -> Conversation:
    """Get existing conversation or create a new one."""
    conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()

    if not conversation:
        conversation = Conversation(
            wa_id=wa_id,
            state="awaiting_name",
            language="en",
            turn_count=0,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Created new conversation for {wa_id}")

    return conversation


def load_conversation_history(db: Session, wa_id: str, max_turns: int = 10) -> list:
    """Load conversation history for the agent context."""
    messages = db.query(Message).filter_by(wa_id=wa_id).order_by(Message.created_at.desc()).limit(max_turns * 2).all()
    messages.reverse()

    history = []
    for msg in messages:
        role = "user" if msg.direction == "inbound" else "assistant"
        history.append({
            "role": role,
            "content": msg.body or "[Non-text message]"
        })

    return history


def save_message(
    db: Session,
    wa_id: str,
    direction: str,
    message_type: str,
    body: str,
    meta_message_id: str = None,
) -> Message:
    """Save a message to the audit log."""
    message = Message(
        wa_id=wa_id,
        direction=direction,
        message_type=message_type,
        body=body,
        meta_message_id=meta_message_id,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def update_conversation_state(
    db: Session,
    wa_id: str,
    state: str,
    language: str = None,
    current_booking_id: int = None,
) -> Conversation:
    """Update conversation state."""
    conversation = db.query(Conversation).filter_by(wa_id=wa_id).first()

    if conversation:
        conversation.state = state
        conversation.last_message_at = datetime.now()
        conversation.turn_count += 1

        if language:
            conversation.language = language
        if current_booking_id:
            conversation.current_booking_id = current_booking_id

        db.commit()
        db.refresh(conversation)

    return conversation


def get_patient_or_create(db: Session, wa_id: str) -> Patient:
    """Get or create a patient by WhatsApp ID."""
    patient = db.query(Patient).filter_by(wa_id=wa_id).first()

    if not patient:
        patient = Patient(wa_id=wa_id)
        db.add(patient)
        db.commit()
        db.refresh(patient)
        logger.info(f"Created new patient record for {wa_id}")

    return patient
