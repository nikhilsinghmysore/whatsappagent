from pydantic import BaseModel
from typing import Optional, Any, List, Dict


class TextMessage(BaseModel):
    body: str


class TemplateButton(BaseModel):
    type: str
    text: str


class InteractiveMessage(BaseModel):
    type: str
    button_reply: Optional[Dict[str, str]] = None
    list_reply: Optional[Dict[str, str]] = None


class LocationData(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None


class ImageData(BaseModel):
    id: str
    mime_type: str


class AudioData(BaseModel):
    id: str
    mime_type: str
    voice: Optional[bool] = None


class Message(BaseModel):
    id: str
    timestamp: str
    type: str
    from_field: str = None  # 'from' is reserved, use 'from_field'
    text: Optional[TextMessage] = None
    interactive: Optional[InteractiveMessage] = None
    location: Optional[LocationData] = None
    image: Optional[ImageData] = None
    audio: Optional[AudioData] = None

    class Config:
        populate_by_name = True
        fields = {"from_field": {"alias": "from"}}


class StatusUpdate(BaseModel):
    id: str
    status: str
    timestamp: str
    recipient_id: str


class Contact(BaseModel):
    wa_id: str
    profile: Dict[str, Any]


class WebhookEntry(BaseModel):
    id: str
    changes: List[Dict[str, Any]]


class WebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]
