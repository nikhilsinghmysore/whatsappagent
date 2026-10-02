from typing import Optional, List, Dict, Any
from src.whatsapp.types import Message


def parse_webhook_messages(data: Dict[str, Any]) -> List[tuple[str, Message, Optional[str]]]:
    """
    Parse incoming webhook and extract messages.
    Returns list of (wa_id, Message, meta_message_id).
    """
    messages = []

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for msg in value.get("messages", []):
                    wa_id = msg.get("from")
                    message_id = msg.get("id")

                    message = Message(
                        id=message_id,
                        timestamp=msg.get("timestamp", ""),
                        type=msg.get("type", "text"),
                        from_field=wa_id,
                        text={"body": msg.get("text", {}).get("body")} if msg.get("type") == "text" else None,
                        interactive=msg.get("interactive") if msg.get("type") == "interactive" else None,
                        location=msg.get("location") if msg.get("type") == "location" else None,
                        image=msg.get("image") if msg.get("type") == "image" else None,
                        audio=msg.get("audio") if msg.get("type") == "audio" else None,
                    )

                    messages.append((wa_id, message, message_id))
    except Exception as e:
        print(f"Error parsing webhook: {e}")

    return messages
