#!/usr/bin/env python3
"""Simulate WhatsApp webhook messages for testing."""

import requests
import json
import hmac
import hashlib
from datetime import datetime

# Get your ngrok URL
WEBHOOK_URL = "https://nugget-symphonic-grab.ngrok-free.dev/webhook"
VERIFY_TOKEN = "test-verify-token"
APP_SECRET = "test-secret-for-testing"

def generate_signature(body: str) -> str:
    """Generate X-Hub-Signature for webhook verification."""
    signature = hmac.new(
        APP_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def send_test_message(wa_id: str, message_text: str):
    """Send a test WhatsApp message to your webhook."""

    timestamp = str(int(datetime.now().timestamp()))

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1773667110450602",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919876543210",
                                "phone_number_id": "1334321436434182",
                            },
                            "messages": [
                                {
                                    "from": wa_id,
                                    "id": f"msg_{timestamp}",
                                    "timestamp": timestamp,
                                    "type": "text",
                                    "text": {
                                        "body": message_text
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

    body = json.dumps(payload)
    signature = generate_signature(body)

    headers = {
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json",
    }

    print(f"\n📤 Sending test message from {wa_id}:")
    print(f"   Message: '{message_text}'")

    response = requests.post(WEBHOOK_URL, data=body, headers=headers)

    print(f"   Status: {response.status_code}")
    if response.text:
        print(f"   Response: {response.text}\n")

    return response

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python test_webhook.py <wa_id> <message>")
        print("\nExample:")
        print('  python test_webhook.py 919999999999 "I need to book a doctor"')
        print('  python test_webhook.py 919999999999 "I have a fever"')
        sys.exit(1)

    wa_id = sys.argv[1]
    message = " ".join(sys.argv[2:])

    send_test_message(wa_id, message)
