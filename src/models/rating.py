from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric
from src.db import BaseModel


class Rating(BaseModel):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    patient_wa_id = Column(String(20), ForeignKey("patients.wa_id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    feedback_text = Column(Text, nullable=True)
