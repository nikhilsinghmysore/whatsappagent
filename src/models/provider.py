from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, Numeric
from src.db import BaseModel


class Provider(BaseModel):
    __tablename__ = "providers"

    wa_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # doctor_visit, nurse_visit, etc
    registration_no = Column(String(100), unique=True, nullable=False)
    verification_status = Column(String(20), default="pending", nullable=False, index=True)  # pending, approved, rejected
    fee = Column(Numeric(10, 2), nullable=True)
    service_area = Column(JSON, nullable=True)  # List of pin codes or location identifiers
    is_online = Column(Boolean, default=False, nullable=False)
    availability = Column(JSON, nullable=True)  # {day: [start_time, end_time]}
    rating_avg = Column(Numeric(3, 2), default=0, nullable=False)
    total_bookings = Column(Integer, default=0, nullable=False)
    bio = Column(Text, nullable=True)
