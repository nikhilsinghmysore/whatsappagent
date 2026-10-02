from sqlalchemy import Column, String, Text
from src.db import BaseModel


class Service(BaseModel):
    __tablename__ = "services"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # doctor_visit, nurse_visit, etc
