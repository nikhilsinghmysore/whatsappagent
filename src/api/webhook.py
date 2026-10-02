from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, status
from src.whatsapp.signature import verify_signature
from src.whatsapp.parser import parse_webhook_messages
from src.config import settings
from src.whatsapp.client import WhatsAppClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])

whatsapp_client = WhatsAppClient()


@router.get("/")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None,
):
    """Meta webhook verification (GET request)."""
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="Invalid mode")

    if hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="Invalid verify token")

    return {"hub_challenge": hub_challenge}


@router.post("/")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """Receive incoming messages from WhatsApp (POST request)."""
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    # Verify signature
    if not verify_signature(body.decode(), signature):
        logger.warning("Invalid signature received")
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse JSON
    data = await request.json()

    # Deduplicate and parse messages
    try:
        messages = parse_webhook_messages(data)

        for wa_id, message, meta_message_id in messages:
            logger.info(f"Received message from {wa_id}: {message.type}")
            # Queue for background processing
            background_tasks.add_task(
                process_message, wa_id, message, meta_message_id
            )
    except Exception as e:
        logger.error(f"Error parsing webhook: {e}")

    # Return 200 immediately
    return {"status": "ok"}


async def process_message(wa_id: str, message, meta_message_id: str):
    """
    Process incoming message in background.
    This is a placeholder for now; will be replaced with actual agent logic.
    """
    logger.info(f"Processing message {meta_message_id} from {wa_id}")

    try:
        # Mark as read
        await whatsapp_client.mark_as_read(message.id)

        # For now, just echo the message back
        if message.text:
            await whatsapp_client.send_text_message(
                wa_id,
                f"Echo: {message.text.body}"
            )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
