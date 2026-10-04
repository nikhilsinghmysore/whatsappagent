"""OpenAI API client with tool use for booking agent."""

import json
import logging
from openai import OpenAI
from sqlalchemy.orm import Session
from src.config import settings
from src.agent.prompts import SYSTEM_PROMPT, EMERGENCY_KEYWORDS
from src.agent import tools

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_providers",
            "description": "Search for available providers by service type, location (pin code), and date",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_category": {"type": "string", "description": "Service category"},
                    "pin_code": {"type": "string", "description": "Patient's pin code"},
                    "scheduled_date": {"type": "string", "description": "Preferred date (YYYY-MM-DD)"},
                },
                "required": ["service_category", "pin_code", "scheduled_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a new booking for a patient with a selected provider",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_wa_id": {"type": "string"},
                    "service_category": {"type": "string"},
                    "provider_id": {"type": "integer"},
                    "symptoms": {"type": "string"},
                    "address": {"type": "string"},
                    "pin_code": {"type": "string"},
                    "scheduled_date": {"type": "string"},
                    "scheduled_time": {"type": "string"},
                },
                "required": ["patient_wa_id", "service_category", "provider_id", "symptoms", "address", "pin_code", "scheduled_date", "scheduled_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_booking",
            "description": "Get details and status of an existing booking",
            "parameters": {"type": "object", "properties": {"booking_id": {"type": "integer"}}, "required": ["booking_id"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Cancel an existing booking",
            "parameters": {"type": "object", "properties": {"booking_id": {"type": "integer"}}, "required": ["booking_id"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_booking",
            "description": "Reschedule a booking to a new date and time",
            "parameters": {
                "type": "object",
                "properties": {"booking_id": {"type": "integer"}, "new_date": {"type": "string"}, "new_time": {"type": "string"}},
                "required": ["booking_id", "new_date", "new_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human admin",
            "parameters": {
                "type": "object",
                "properties": {"wa_id": {"type": "string"}, "reason": {"type": "string"}},
                "required": ["wa_id", "reason"],
            },
        },
    },
]


def check_emergency_keywords(message: str) -> str:
    """Check if message contains emergency keywords."""
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
    """Process a message using OpenAI agent with tool use."""

    emergency = check_emergency_keywords(message_text)
    if emergency:
        logger.warning(f"Emergency detected from {wa_id}: {emergency}")
        tools.escalate_to_human(db, wa_id, f"Emergency: {emergency}")
        return "🚨 EMERGENCY DETECTED\n\nPlease call 108 immediately or go to the nearest hospital.\n\nHome Clinic is a booking platform only. We are connecting you with a human agent for immediate support."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Filter out any messages with null content
    for msg in conversation_history:
        if msg.get("content") or (msg.get("role") == "assistant" and msg.get("tool_calls")):
            messages.append(msg)
    messages.append({"role": "user", "content": message_text})

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=1024,
    )

    while response.choices[0].finish_reason == "tool_calls":
        tool_call = response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_input = json.loads(tool_call.function.arguments)

        logger.info(f"Agent calling tool: {tool_name}")

        try:
            if tool_name == "search_providers":
                result = tools.search_providers(db, tool_input["service_category"], tool_input["pin_code"], tool_input["scheduled_date"])
            elif tool_name == "create_booking":
                result = tools.create_booking(db, tool_input["patient_wa_id"], tool_input["service_category"], tool_input["provider_id"], tool_input["symptoms"], tool_input["address"], tool_input["pin_code"], tool_input["scheduled_date"], tool_input["scheduled_time"])
            elif tool_name == "get_booking":
                result = tools.get_booking(db, tool_input["booking_id"])
            elif tool_name == "cancel_booking":
                result = tools.cancel_booking(db, tool_input["booking_id"])
            elif tool_name == "reschedule_booking":
                result = tools.reschedule_booking(db, tool_input["booking_id"], tool_input["new_date"], tool_input["new_time"])
            elif tool_name == "escalate_to_human":
                result = tools.escalate_to_human(db, tool_input["wa_id"], tool_input["reason"])
            else:
                result = json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            result = json.dumps({"error": str(e)})

        assistant_msg = {"role": "assistant", "tool_calls": response.choices[0].message.tool_calls}
        if response.choices[0].message.content:
            assistant_msg["content"] = response.choices[0].message.content
        messages.append(assistant_msg)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024,
        )

    return response.choices[0].message.content or ""
