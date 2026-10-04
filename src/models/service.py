from sqlalchemy import Column, String, Text, Integer
from src.db import BaseModel


class Service(BaseModel):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # doctor_visit, nurse_visit, etc
