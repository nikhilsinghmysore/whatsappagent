from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON
from src.db import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"

    wa_id = Column(String(20), unique=True, nullable=False, index=True, primary_key=True)
    state = Column(String(50), default="awaiting_name", nullable=False)
    # awaiting_name, awaiting_service, awaiting_address, awaiting_date, awaiting_confirmation, completed, escalated
    language = Column(String(10), default="en", nullable=False)
    current_booking_id = Column(Integer, nullable=True)
    turn_count = Column(Integer, default=0, nullable=False)
    escalated_to_human_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    is_escalated = Column(Boolean, default=False, nullable=False)
    summary = Column(Text, nullable=True)  # Summarized context for old turns
    reminder_preference = Column(JSON, nullable=True)  # {hours_before: 24, enabled: true}
