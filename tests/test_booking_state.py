"""Tests for booking state machine."""

import pytest
from src.models.booking import Booking
from src.models.patient import Patient
from src.models.provider import Provider
from src.models.service import Service


@pytest.fixture
def booking_setup(db_session):
    """Set up test data for bookings."""
    patient = Patient(wa_id="919999999999")
    service = Service(name="Doctor", category="doctor_visit")
    provider = Provider(
        wa_id="919888888888",
        name="Dr. Test",
        category="doctor_visit",
        registration_no="REG123",
        verification_status="approved",
    )

    db_session.add_all([patient, service, provider])
    db_session.commit()

    return {"patient": patient, "service": service, "provider": provider}


def test_booking_initial_state(db_session, booking_setup):
    """Test that new bookings start in 'requested' state."""
    booking = Booking(
        patient_wa_id=booking_setup["patient"].wa_id,
        provider_id=booking_setup["provider"].id,
        service_id=booking_setup["service"].id,
    )
    db_session.add(booking)
    db_session.commit()

    assert booking.status == "requested"


def test_booking_state_transition(db_session, booking_setup):
    """Test valid state transitions."""
    booking = Booking(
        patient_wa_id=booking_setup["patient"].wa_id,
        provider_id=booking_setup["provider"].id,
        service_id=booking_setup["service"].id,
        status="requested",
    )
    db_session.add(booking)
    db_session.commit()

    # Transition: requested -> provider_assigned
    booking.status = "provider_assigned"
    db_session.commit()
    db_session.refresh(booking)
    assert booking.status == "provider_assigned"

    # Transition: provider_assigned -> accepted
    booking.status = "accepted"
    db_session.commit()
    db_session.refresh(booking)
    assert booking.status == "accepted"

    # Transition: accepted -> en_route
    booking.status = "en_route"
    db_session.commit()
    db_session.refresh(booking)
    assert booking.status == "en_route"

    # Transition: en_route -> completed
    booking.status = "completed"
    db_session.commit()
    db_session.refresh(booking)
    assert booking.status == "completed"


def test_booking_cancellation(db_session, booking_setup):
    """Test cancellation from various states."""
    booking = Booking(
        patient_wa_id=booking_setup["patient"].wa_id,
        provider_id=booking_setup["provider"].id,
        service_id=booking_setup["service"].id,
        status="requested",
    )
    db_session.add(booking)
    db_session.commit()

    # Cancel from requested state
    booking.status = "cancelled"
    db_session.commit()
    db_session.refresh(booking)
    assert booking.status == "cancelled"


def test_booking_without_provider(db_session, booking_setup):
    """Test booking without assigned provider."""
    booking = Booking(
        patient_wa_id=booking_setup["patient"].wa_id,
        service_id=booking_setup["service"].id,
        status="requested",
    )
    db_session.add(booking)
    db_session.commit()

    assert booking.provider_id is None
    assert booking.status == "requested"
