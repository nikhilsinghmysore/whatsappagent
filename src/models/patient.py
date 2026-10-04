from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from src.db import BaseModel


class Patient(BaseModel):
    __tablename__ = "patients"

    wa_id = Column(String(20), primary_key=True, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    language = Column(String(10), default="en", nullable=False)
    default_address = Column(Text, nullable=True)
    pin = Column(String(10), nullable=True)
    consent_opt_in_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
