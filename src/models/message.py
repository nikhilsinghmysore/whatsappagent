from sqlalchemy import Column, String, Text, Boolean
from src.db import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"

    wa_id = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # inbound, outbound
    message_type = Column(String(20), nullable=False)  # text, interactive, location, image, audio
    body = Column(Text, nullable=True)
    meta_message_id = Column(String(100), unique=True, nullable=True)
    is_duplicate = Column(Boolean, default=False, nullable=False)
    error = Column(Text, nullable=True)
