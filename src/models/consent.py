from sqlalchemy import Column, String, Boolean, DateTime, Integer
from src.db import BaseModel


class Consent(BaseModel):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wa_id = Column(String(20), nullable=False, index=True)
    template_name = Column(String(100), nullable=False)
    opted_in = Column(Boolean, default=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
