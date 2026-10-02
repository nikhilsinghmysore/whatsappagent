import hmac
import hashlib
from src.config import settings


def verify_signature(body: str, signature: str) -> bool:
    """Verify X-Hub-Signature-256 header from Meta."""
    expected_signature = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
