from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from src.db import BaseModel


class Booking(BaseModel):
    __tablename__ = "bookings"

    patient_wa_id = Column(String(20), ForeignKey("patients.wa_id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String(20), default="requested", nullable=False, index=True)
    # requested -> provider_assigned -> accepted -> en_route -> completed -> cancelled
    symptoms = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    pin = Column(String(10), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    provider_response_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    meta_message_id = Column(String(100), unique=True, nullable=True)
    notes = Column(Text, nullable=True)
