"""Tests for agent tool functions."""

import pytest
from src.agent.tools import (
    search_providers,
    create_booking,
    get_booking,
    cancel_booking,
)
from src.models.provider import Provider
from src.models.patient import Patient
from src.models.service import Service


@pytest.fixture
def setup_data(db_session):
    """Create test data."""
    # Create service
    service = Service(
        name="Doctor Visit",
        category="doctor_visit",
        description="Home doctor visit",
    )
    db_session.add(service)
    db_session.flush()

    # Create patient
    patient = Patient(wa_id="919999999999", name="Test Patient", age=30)
    db_session.add(patient)
    db_session.flush()

    # Create provider
    provider = Provider(
        wa_id="919888888888",
        name="Dr. Test",
        category="doctor_visit",
        registration_no="REG123",
        verification_status="approved",
        fee=500,
        service_area=["570001"],
        is_online=True,
    )
    db_session.add(provider)
    db_session.commit()

    return {
        "service": service,
        "patient": patient,
        "provider": provider,
    }


def test_search_providers(db_session, setup_data):
    """Test searching for providers."""
    result_str = search_providers(
        db_session,
        "doctor_visit",
        "570001",
        "2024-01-15",
    )

    import json
    result = json.loads(result_str)

    assert result["success"] is True
    assert result["count"] > 0
    assert len(result["providers"]) > 0


def test_search_providers_no_match(db_session):
    """Test searching with no matching providers."""
    result_str = search_providers(
        db_session,
        "doctor_visit",
        "999999",  # No provider in this area
        "2024-01-15",
    )

    import json
    result = json.loads(result_str)

    assert "error" in result


def test_create_booking(db_session, setup_data):
    """Test booking creation."""
    result_str = create_booking(
        db_session,
        "919999999999",
        "doctor_visit",
        setup_data["provider"].id,
        "Fever and cold",
        "123 Main St",
        "570001",
        "2024-01-15",
        "14:00",
    )

    import json
    result = json.loads(result_str)

    assert result["success"] is True
    assert result["booking_id"] is not None
    assert result["status"] == "requested"


def test_get_booking(db_session, setup_data):
    """Test retrieving booking details."""
    # Create a booking first
    from src.models.booking import Booking
    booking = Booking(
        patient_wa_id="919999999999",
        provider_id=setup_data["provider"].id,
        service_id=setup_data["service"].id,
        status="requested",
        address="123 Main St",
        pin="570001",
    )
    db_session.add(booking)
    db_session.commit()

    result_str = get_booking(db_session, booking.id)

    import json
    result = json.loads(result_str)

    assert result["success"] is True
    assert result["booking_id"] == booking.id
    assert result["status"] == "requested"


def test_cancel_booking(db_session, setup_data):
    """Test booking cancellation."""
    # Create a booking first
    from src.models.booking import Booking
    booking = Booking(
        patient_wa_id="919999999999",
        provider_id=setup_data["provider"].id,
        service_id=setup_data["service"].id,
        status="requested",
        address="123 Main St",
        pin="570001",
    )
    db_session.add(booking)
    db_session.commit()

    result_str = cancel_booking(db_session, booking.id)

    import json
    result = json.loads(result_str)

    assert result["success"] is True
    assert result["status"] == "cancelled"

    # Verify status in DB
    db_session.refresh(booking)
    assert booking.status == "cancelled"
