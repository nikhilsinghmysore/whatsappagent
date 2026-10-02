"""Tests for admin API endpoints."""

import pytest
import jwt
from src.config import settings
from src.models.provider import Provider
from src.models.booking import Booking
from src.models.patient import Patient
from src.models.service import Service
from src.models.conversation import Conversation


def generate_admin_token():
    """Generate a valid admin token for testing."""
    payload = {"admin": True}
    return jwt.encode(
        payload,
        settings.admin_jwt_secret,
        algorithm=settings.admin_jwt_algorithm,
    )


@pytest.fixture
def admin_token():
    return generate_admin_token()


def test_approve_provider(client, db_session, admin_token):
    """Test provider approval."""
    provider = Provider(
        wa_id="919888888888",
        name="Dr. Test",
        category="doctor_visit",
        registration_no="REG123",
        verification_status="pending",
    )
    db_session.add(provider)
    db_session.commit()

    response = client.post(
        f"/admin/providers/{provider.id}/approve?token={admin_token}"
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    db_session.refresh(provider)
    assert provider.verification_status == "approved"


def test_list_bookings(client, db_session, admin_token):
    """Test listing bookings."""
    patient = Patient(wa_id="919999999999")
    service = Service(name="Doctor", category="doctor_visit")
    provider = Provider(
        wa_id="919888888888",
        name="Dr. Test",
        category="doctor_visit",
        registration_no="REG123",
        verification_status="approved",
    )

    booking = Booking(
        patient_wa_id=patient.wa_id,
        provider_id=provider.id,
        service_id=service.id,
        status="requested",
    )

    db_session.add_all([patient, service, provider, booking])
    db_session.commit()

    response = client.get(f"/admin/bookings?token={admin_token}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["bookings"]) > 0


def test_get_conversation(client, db_session, admin_token):
    """Test retrieving conversation details."""
    conversation = Conversation(wa_id="919999999999")
    db_session.add(conversation)
    db_session.commit()

    response = client.get(f"/admin/conversations/919999999999?token={admin_token}")

    assert response.status_code == 200
    data = response.json()
    assert data["wa_id"] == "919999999999"


def test_takeover_conversation(client, db_session, admin_token):
    """Test admin takeover of conversation."""
    conversation = Conversation(wa_id="919999999999", is_escalated=False)
    db_session.add(conversation)
    db_session.commit()

    response = client.post(
        f"/admin/conversations/919999999999/takeover?token={admin_token}"
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    db_session.refresh(conversation)
    assert conversation.is_escalated is True


def test_missing_token(client):
    """Test that missing token returns 401."""
    response = client.get("/admin/bookings")
    assert response.status_code == 401


def test_invalid_token(client):
    """Test that invalid token returns 401."""
    response = client.get("/admin/bookings?token=invalid_token")
    assert response.status_code == 401
