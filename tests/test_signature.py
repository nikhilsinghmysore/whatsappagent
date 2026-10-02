import hmac
import hashlib
from src.config import settings
from src.whatsapp.signature import verify_signature


def test_verify_signature_valid():
    """Test signature verification with valid signature."""
    body = '{"test": "data"}'
    signature = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    assert verify_signature(body, f"sha256={signature}") is True


def test_verify_signature_invalid():
    """Test signature verification with invalid signature."""
    body = '{"test": "data"}'
    assert verify_signature(body, "sha256=invalid") is False


def test_verify_signature_tampered_body():
    """Test signature verification with tampered body."""
    body = '{"test": "data"}'
    signature = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    tampered_body = '{"test": "modified"}'
    assert verify_signature(tampered_body, f"sha256={signature}") is False
