from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.whatsapp.signature import verify_signature
from src.whatsapp.parser import parse_webhook_messages
from src.config import settings
from src.whatsapp.client import WhatsAppClient
from src.db.connection import SessionLocal
from src.agent.claude import process_message_with_agent
from src.agent.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    save_message,
    get_patient_or_create,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhook"])

whatsapp_client = WhatsAppClient()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None,
):
    """Meta webhook verification (GET request)."""
    logger.info(f"Webhook verification: mode={hub_mode}, challenge={hub_challenge}, token={hub_verify_token}")
    logger.info(f"Expected token: {settings.whatsapp_verify_token}")

    if hub_mode != "subscribe":
        logger.error(f"Invalid mode: {hub_mode}")
        raise HTTPException(status_code=400, detail="Invalid mode")

    if hub_verify_token != settings.whatsapp_verify_token:
        logger.error(f"Token mismatch: received={hub_verify_token}")
        raise HTTPException(status_code=403, detail="Invalid verify token")

    logger.info(f"✅ Webhook verification successful")
    # Return plain text, not JSON (Meta requirement)
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(hub_challenge)


@router.post("/webhook")
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
            background_tasks.add_task(
                process_message, wa_id, message, meta_message_id
            )
    except Exception as e:
        logger.error(f"Error parsing webhook: {e}")

    return {"status": "ok"}


async def process_message(wa_id: str, message, meta_message_id: str):
    """Process incoming message with Claude agent."""
    logger.info(f"Processing message {meta_message_id} from {wa_id}")

    db = SessionLocal()

    try:
        # Mark as read
        await whatsapp_client.mark_as_read(message.id)

        # Get or create patient and conversation
        patient = get_patient_or_create(db, wa_id)
        conversation = get_or_create_conversation(db, wa_id)

        # Save incoming message
        save_message(
            db,
            wa_id,
            "inbound",
            message.type,
            message.text.body if message.text else None,
            meta_message_id,
        )

        # Check if conversation is escalated (human takeover)
        if conversation.is_escalated:
            logger.info(f"Conversation {wa_id} is escalated. Waiting for human.")
            return

        # Load conversation history
        history = load_conversation_history(db, wa_id)

        # Show typing indicator
        await whatsapp_client.send_typing_indicator(wa_id)

        # Process with Claude agent
        message_text = message.text.body if message.text else "[Non-text message]"
        response_text = await process_message_with_agent(
            db,
            wa_id,
            message_text,
            history,
        )

        # Save outgoing message
        save_message(
            db,
            wa_id,
            "outbound",
            "text",
            response_text,
        )

        # Send response
        await whatsapp_client.send_text_message(wa_id, response_text)

    except Exception as e:
        logger.error(f"Error processing message {meta_message_id}: {e}", exc_info=True)
        try:
            await whatsapp_client.send_text_message(
                wa_id,
                "Sorry, I encountered an error. Please try again or contact support."
            )
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")
    finally:
        db.close()
