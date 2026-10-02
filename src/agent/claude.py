"""Claude API client with tool use for booking agent."""

import json
import logging
from anthropic import Anthropic
from sqlalchemy.orm import Session
from src.config import settings
from src.agent.prompts import SYSTEM_PROMPT, EMERGENCY_KEYWORDS
from src.agent import tools

logger = logging.getLogger(__name__)

client = Anthropic(api_key=settings.anthropic_api_key)

TOOLS = [
    {
        "name": "search_providers",
        "description": "Search for available providers by service type, location (pin code), and date",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_category": {
                    "type": "string",
                    "description": "Service category: doctor_visit, nurse_visit, injection, wound_care, elderly_care, sample_collection",
                },
                "pin_code": {
                    "type": "string",
                    "description": "Patient's pin code",
                },
                "scheduled_date": {
                    "type": "string",
                    "description": "Preferred date (YYYY-MM-DD)",
                },
            },
            "required": ["service_category", "pin_code", "scheduled_date"],
        },
    },
    {
        "name": "create_booking",
        "description": "Create a new booking for a patient with a selected provider",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_wa_id": {"type": "string", "description": "Patient WhatsApp ID"},
                "service_category": {"type": "string", "description": "Service category"},
                "provider_id": {"type": "integer", "description": "Selected provider ID"},
                "symptoms": {"type": "string", "description": "Brief description of symptoms/needs"},
                "address": {"type": "string", "description": "Patient's address"},
                "pin_code": {"type": "string", "description": "Pin code"},
                "scheduled_date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                "scheduled_time": {"type": "string", "description": "Time (HH:MM)"},
            },
            "required": [
                "patient_wa_id",
                "service_category",
                "provider_id",
                "symptoms",
                "address",
                "pin_code",
                "scheduled_date",
                "scheduled_time",
            ],
        },
    },
    {
        "name": "get_booking",
        "description": "Get details and status of an existing booking",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "integer", "description": "Booking ID"},
            },
            "required": ["booking_id"],
        },
    },
    {
        "name": "cancel_booking",
        "description": "Cancel an existing booking",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "integer", "description": "Booking ID to cancel"},
            },
            "required": ["booking_id"],
        },
    },
    {
        "name": "reschedule_booking",
        "description": "Reschedule a booking to a new date and time",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "integer", "description": "Booking ID"},
                "new_date": {"type": "string", "description": "New date (YYYY-MM-DD)"},
                "new_time": {"type": "string", "description": "New time (HH:MM)"},
            },
            "required": ["booking_id", "new_date", "new_time"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the conversation to a human admin for complex issues",
        "input_schema": {
            "type": "object",
            "properties": {
                "wa_id": {"type": "string", "description": "Patient WhatsApp ID"},
                "reason": {"type": "string", "description": "Reason for escalation"},
            },
            "required": ["wa_id", "reason"],
        },
    },
]


def check_emergency_keywords(message: str) -> str:
    """Check if message contains emergency keywords. Returns category or None."""
    message_lower = message.lower()
    for category, keywords in EMERGENCY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return category
    return None


async def process_message_with_agent(
    db: Session,
    wa_id: str,
    message_text: str,
    conversation_history: list,
) -> str:
    """
    Process a message using Claude agent with tool use.
    Returns the agent's response text.
    """

    # Check for emergency keywords
    emergency = check_emergency_keywords(message_text)
    if emergency:
        logger.warning(f"Emergency detected from {wa_id}: {emergency}")
        emergency_response = (
            "🚨 EMERGENCY DETECTED\n\n"
            "Please call 108 immediately or go to the nearest hospital.\n\n"
            "Home Clinic is a booking platform only. We are connecting you with a human agent for immediate support."
        )
        # Escalate to human
        tools.escalate_to_human(db, wa_id, f"Emergency: {emergency}")
        return emergency_response

    # Build conversation messages
    messages = conversation_history.copy()
    messages.append({"role": "user", "content": message_text})

    # Initial call to Claude
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    # Process tool use in a loop
    while response.stop_reason == "tool_use":
        # Find tool use block
        tool_use_block = next(
            (block for block in response.content if block.type == "tool_use"),
            None,
        )

        if not tool_use_block:
            break

        tool_name = tool_use_block.name
        tool_input = tool_use_block.input
        tool_use_id = tool_use_block.id

        logger.info(f"Agent calling tool: {tool_name}")

        # Execute tool
        try:
            if tool_name == "search_providers":
                result = tools.search_providers(
                    db,
                    tool_input["service_category"],
                    tool_input["pin_code"],
                    tool_input["scheduled_date"],
                )
            elif tool_name == "create_booking":
                result = tools.create_booking(
                    db,
                    tool_input["patient_wa_id"],
                    tool_input["service_category"],
                    tool_input["provider_id"],
                    tool_input["symptoms"],
                    tool_input["address"],
                    tool_input["pin_code"],
                    tool_input["scheduled_date"],
                    tool_input["scheduled_time"],
                )
            elif tool_name == "get_booking":
                result = tools.get_booking(db, tool_input["booking_id"])
            elif tool_name == "cancel_booking":
                result = tools.cancel_booking(db, tool_input["booking_id"])
            elif tool_name == "reschedule_booking":
                result = tools.reschedule_booking(
                    db,
                    tool_input["booking_id"],
                    tool_input["new_date"],
                    tool_input["new_time"],
                )
            elif tool_name == "escalate_to_human":
                result = tools.escalate_to_human(
                    db,
                    tool_input["wa_id"],
                    tool_input["reason"],
                )
            else:
                result = json.dumps({"error": f"Unknown tool: {tool_name}"})

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            result = json.dumps({"error": str(e)})

        # Add assistant response and tool result to messages
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": result,
                }
            ],
        })

        # Continue conversation
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    # Extract final text response
    text_blocks = [block for block in response.content if hasattr(block, "text")]
    final_response = "\n".join([block.text for block in text_blocks])

    return final_response
