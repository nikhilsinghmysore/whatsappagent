from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from src.db import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)  # id_proof, license, certificate, etc
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(50), nullable=False)
    data = Column(LargeBinary, nullable=False)  # Base64 encoded image
    verified = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
