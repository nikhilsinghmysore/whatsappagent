import httpx
from typing import Optional, Dict, Any, List
from src.config import settings
import json


class WhatsAppClient:
    def __init__(self):
        self.api_version = settings.whatsapp_api_version
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.token = settings.whatsapp_api_token
        self.base_url = f"https://graph.instagram.com/{self.api_version}"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(
        self, recipient_wa_id: str, text: str
    ) -> Dict[str, Any]:
        """Send a text message."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_wa_id,
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
        return response.json()

    async def send_interactive_buttons(
        self,
        recipient_wa_id: str,
        body: str,
        buttons: List[Dict[str, str]],
        header: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message with interactive buttons."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        interactive_obj = {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"]}}
                    for btn in buttons
                ]
            },
        }

        if header:
            interactive_obj["header"] = {"type": "text", "text": header}
        if footer:
            interactive_obj["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_wa_id,
            "type": "interactive",
            "interactive": interactive_obj,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
        return response.json()

    async def send_interactive_list(
        self,
        recipient_wa_id: str,
        body: str,
        sections: List[Dict[str, Any]],
        button_text: str = "Choose",
        header: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message with an interactive list."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        interactive_obj = {
            "type": "list",
            "body": {"text": body},
            "action": {
                "button": button_text,
                "sections": sections,
            },
        }

        if header:
            interactive_obj["header"] = {"type": "text", "text": header}
        if footer:
            interactive_obj["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_wa_id,
            "type": "interactive",
            "interactive": interactive_obj,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
        return response.json()

    async def send_template_message(
        self,
        recipient_wa_id: str,
        template_name: str,
        language: str = "en",
        parameters: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Send an approved template message."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_wa_id,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            },
        }

        if parameters:
            payload["template"]["components"] = [
                {
                    "type": "body",
                    "parameters": parameters,
                }
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
        return response.json()

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
        return response.json()

    async def send_typing_indicator(self, recipient_wa_id: str) -> Dict[str, Any]:
        """Send a typing indicator."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_wa_id,
            "type": "typing",
            "typing": {"is_typing": True},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
        return response.json()
