import json
import hmac
import hashlib
from src.config import settings


def test_webhook_get_verification(client):
    """Test GET webhook verification (Meta handshake)."""
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge",
            "hub.verify_token": settings.whatsapp_verify_token,
        }
    )

    assert response.status_code == 200
    assert response.json() == {"hub_challenge": "test_challenge"}


def test_webhook_get_invalid_token(client):
    """Test GET webhook with invalid verify token."""
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge",
            "hub.verify_token": "invalid_token",
        }
    )

    assert response.status_code == 403


def test_webhook_post_invalid_signature(client):
    """Test POST webhook with invalid signature."""
    payload = {"object": "whatsapp_business_account"}
    body = json.dumps(payload)

    response = client.post(
        "/webhook",
        data=body,
        headers={"x-hub-signature-256": "sha256=invalid"}
    )

    assert response.status_code == 403


def test_webhook_post_valid_signature(client):
    """Test POST webhook with valid signature."""
    payload = {"object": "whatsapp_business_account", "entry": []}
    body = json.dumps(payload)

    signature = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        "/webhook",
        data=body,
        headers={"x-hub-signature-256": f"sha256={signature}"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
