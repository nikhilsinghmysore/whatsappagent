"""Provider management service."""

import json
import logging
from sqlalchemy.orm import Session
from src.models.provider import Provider
from src.models.document import Document
from datetime import datetime

logger = logging.getLogger(__name__)


def register_provider(
    db: Session,
    wa_id: str,
    name: str,
    category: str,
    registration_no: str,
    service_area: list,
    fee: float,
    bio: str = None,
) -> Provider:
    """Register a new provider (admin approval required)."""
    provider = Provider(
        wa_id=wa_id,
        name=name,
        category=category,
        registration_no=registration_no,
        verification_status="pending",
        fee=fee,
        service_area=service_area,
        is_online=False,
        bio=bio,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    logger.info(f"Registered provider {wa_id} (pending approval)")
    return provider


def update_provider_availability(
    db: Session,
    provider_id: int,
    availability: dict,
) -> Provider:
    """
    Update provider availability.
    Format: {"Monday": ["09:00", "17:00"], "Tuesday": ["09:00", "17:00"]}
    """
    provider = db.query(Provider).filter_by(id=provider_id).first()
    if provider:
        provider.availability = availability
        db.commit()
        db.refresh(provider)
        logger.info(f"Updated availability for provider {provider_id}")
    return provider


def set_provider_online(db: Session, provider_id: int, is_online: bool) -> Provider:
    """Toggle provider online/offline status."""
    provider = db.query(Provider).filter_by(id=provider_id).first()
    if provider:
        provider.is_online = is_online
        db.commit()
        db.refresh(provider)
        logger.info(f"Provider {provider_id} set to online={is_online}")
    return provider


def store_provider_document(
    db: Session,
    provider_id: int,
    document_type: str,
    filename: str,
    mime_type: str,
    data: bytes,
) -> Document:
    """Store a provider document (ID proof, license, etc.)."""
    document = Document(
        provider_id=provider_id,
        document_type=document_type,
        filename=filename,
        mime_type=mime_type,
        data=data,
        verified="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    logger.info(f"Stored document {document_type} for provider {provider_id}")
    return document


def get_provider_documents(db: Session, provider_id: int) -> list:
    """Get all documents for a provider."""
    documents = db.query(Document).filter_by(provider_id=provider_id).all()
    return documents


def verify_provider_document(
    db: Session,
    document_id: int,
    verified: str,  # "approved" or "rejected"
) -> Document:
    """Verify a provider document."""
    document = db.query(Document).filter_by(id=document_id).first()
    if document:
        document.verified = verified
        db.commit()
        db.refresh(document)
        logger.info(f"Document {document_id} verified as {verified}")
    return document


def search_available_providers(
    db: Session,
    category: str,
    pin_code: str,
) -> list:
    """Search for approved, online providers in a category and area."""
    providers = db.query(Provider).filter(
        Provider.category == category,
        Provider.verification_status == "approved",
        Provider.is_online == True,
    ).all()

    # Filter by service area
    matching = []
    for provider in providers:
        if provider.service_area and pin_code in provider.service_area:
            matching.append(provider)

    return matching


def update_provider_rating(db: Session, provider_id: int) -> float:
    """
    Calculate and update average rating for a provider.
    Returns the new average rating.
    """
    from src.models.rating import Rating

    ratings = db.query(Rating).filter_by(provider_id=provider_id).all()
    if not ratings:
        return 0

    avg_rating = sum(r.rating for r in ratings) / len(ratings)

    provider = db.query(Provider).filter_by(id=provider_id).first()
    if provider:
        provider.rating_avg = avg_rating
        provider.total_bookings = len(ratings)
        db.commit()
        db.refresh(provider)
        logger.info(f"Updated rating for provider {provider_id}: {avg_rating:.1f}")

    return avg_rating
