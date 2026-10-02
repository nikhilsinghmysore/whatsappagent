import logging
from datetime import datetime
from src.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)

whatsapp_client = WhatsAppClient()


async def process_webhook_message(wa_id: str, message_data: dict, meta_message_id: str):
    """Process an incoming webhook message asynchronously."""
    logger.info(f"Processing message {meta_message_id} from {wa_id}")

    try:
        # Mark as read
        await whatsapp_client.mark_as_read(message_data.get("id", meta_message_id))

        # TODO: Agent logic here
        logger.info(f"Message processed: {meta_message_id}")
    except Exception as e:
        logger.error(f"Error processing message {meta_message_id}: {e}")


async def send_reminder(booking_id: int, wa_id: str, provider_name: str, scheduled_time: str):
    """Send a visit reminder to the patient."""
    logger.info(f"Sending reminder for booking {booking_id} to {wa_id}")

    try:
        message = f"Reminder: Your appointment with {provider_name} is scheduled for {scheduled_time}. Please confirm or reschedule if needed."
        await whatsapp_client.send_text_message(wa_id, message)
    except Exception as e:
        logger.error(f"Error sending reminder for booking {booking_id}: {e}")


async def send_provider_request(provider_wa_id: str, patient_name: str, service: str, scheduled_time: str):
    """Send a booking request to a provider."""
    logger.info(f"Sending provider request to {provider_wa_id}")

    try:
        message = f"New booking request: {patient_name} needs {service} on {scheduled_time}. Accept or Reject?"
        # TODO: Send with buttons for Accept/Reject
        await whatsapp_client.send_text_message(provider_wa_id, message)
    except Exception as e:
        logger.error(f"Error sending provider request to {provider_wa_id}: {e}")


async def cleanup_stale_conversations():
    """Clean up old conversation state (hourly task)."""
    logger.info("Cleaning up stale conversations")
    # TODO: Implement
