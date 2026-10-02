"""
Seed database with sample providers for Mysuru.
Run with: python scripts/seed_providers.py
"""

import asyncio
from sqlalchemy.orm import Session
from src.db.connection import SessionLocal, engine
from src.db import Base
from src.models.provider import Provider
from src.models.service import Service
from datetime import datetime


def seed_services():
    """Create service categories."""
    db = SessionLocal()

    services_data = [
        {"name": "Doctor Visit", "category": "doctor_visit", "description": "Home visit by qualified doctor"},
        {"name": "Nurse Care", "category": "nurse_visit", "description": "Home care by trained nurse"},
        {"name": "Injection/IV", "category": "injection", "description": "Injection or IV therapy"},
        {"name": "Wound Dressing", "category": "wound_care", "description": "Professional wound care"},
        {"name": "Elderly Care", "category": "elderly_care", "description": "Care for senior citizens"},
        {"name": "Sample Collection", "category": "sample_collection", "description": "Blood and diagnostic samples"},
    ]

    for service_data in services_data:
        existing = db.query(Service).filter_by(name=service_data["name"]).first()
        if not existing:
            service = Service(**service_data)
            db.add(service)

    db.commit()
    db.close()
    print("✓ Services seeded")


def seed_providers():
    """Create sample providers."""
    db = SessionLocal()

    providers_data = [
        {
            "wa_id": "919876543210",
            "name": "Dr. Rajesh Kumar",
            "category": "doctor_visit",
            "registration_no": "REG12345",
            "verification_status": "approved",
            "fee": 500,
            "service_area": ["570001", "570002"],
            "is_online": True,
            "availability": {"Monday": ["09:00", "17:00"], "Tuesday": ["09:00", "17:00"]},
            "bio": "MBBS, 10 years experience",
        },
        {
            "wa_id": "919876543211",
            "name": "Ms. Anjali Sharma",
            "category": "nurse_visit",
            "registration_no": "REG12346",
            "verification_status": "approved",
            "fee": 300,
            "service_area": ["570001"],
            "is_online": True,
            "availability": {"Monday": ["08:00", "18:00"], "Tuesday": ["08:00", "18:00"]},
            "bio": "Registered Nurse, 5 years experience",
        },
        {
            "wa_id": "919876543212",
            "name": "Dr. Priya Malhotra",
            "category": "doctor_visit",
            "registration_no": "REG12347",
            "verification_status": "approved",
            "fee": 600,
            "service_area": ["570001", "570002", "570003"],
            "is_online": False,
            "availability": {"Monday": ["10:00", "14:00"], "Wednesday": ["10:00", "14:00"]},
            "bio": "MD, Specialist in internal medicine",
        },
        {
            "wa_id": "919876543213",
            "name": "Mr. Suresh Patel",
            "category": "wound_care",
            "registration_no": "REG12348",
            "verification_status": "pending",
            "fee": 250,
            "service_area": ["570001"],
            "is_online": True,
            "bio": "Trained wound care specialist",
        },
    ]

    for provider_data in providers_data:
        existing = db.query(Provider).filter_by(wa_id=provider_data["wa_id"]).first()
        if not existing:
            provider = Provider(**provider_data)
            db.add(provider)

    db.commit()
    db.close()
    print("✓ Providers seeded")


def main():
    print("Seeding database...")
    Base.metadata.create_all(bind=engine)
    seed_services()
    seed_providers()
    print("✓ Database seeded successfully")


if __name__ == "__main__":
    main()
