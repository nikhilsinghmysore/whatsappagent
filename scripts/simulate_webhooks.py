"""
Simulate incoming WhatsApp webhooks for local testing.
Run with: python scripts/simulate_webhooks.py
"""

import json
import hmac
import hashlib
import httpx
import asyncio
from datetime import datetime
from src.config import settings


def generate_signature(body: str) -> str:
    """Generate a valid X-Hub-Signature-256 header."""
    signature = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


async def send_text_message(wa_id: str, text: str):
    """Simulate an incoming text message."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1234567890",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919876543210",
                                "phone_number_id": settings.whatsapp_phone_number_id,
                            },
                            "messages": [
                                {
                                    "from": wa_id,
                                    "id": f"msg_{datetime.now().timestamp()}",
                                    "timestamp": str(int(datetime.now().timestamp())),
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    body = json.dumps(payload)
    signature = generate_signature(body)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/webhook",
            content=body,
            headers={"x-hub-signature-256": signature},
        )
        return response


async def main():
    print("Simulating WhatsApp webhooks...\n")

    # Test 1: Simple greeting
    print("Test 1: Send a greeting message")
    response = await send_text_message("919999999999", "Hello, I need to book a doctor")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    await asyncio.sleep(2)

    # Test 2: Another message
    print("Test 2: Send a follow-up message")
    response = await send_text_message("919999999999", "I have a fever and body ache")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    print("✓ Simulation complete")


if __name__ == "__main__":
    asyncio.run(main())
