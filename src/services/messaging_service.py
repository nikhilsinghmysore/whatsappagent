"""Messaging service with rate limiting and throttling."""

import asyncio
import logging
import time
from typing import Optional
from datetime import datetime, timedelta
import redis
from src.config import settings
from src.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)

# Connect to Redis
try:
    redis_client = redis.from_url(settings.redis_url)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Rate limiting disabled.")
    redis_client = None

whatsapp_client = WhatsAppClient()

# Rate limiting: 1 message per 6 seconds per user
RATE_LIMIT_WINDOW = 6  # seconds
MAX_MESSAGES_PER_WINDOW = 1


def get_rate_limit_key(wa_id: str) -> str:
    """Generate Redis key for rate limiting."""
    return f"rate_limit:{wa_id}"


async def check_rate_limit(wa_id: str) -> bool:
    """Check if user has exceeded rate limit."""
    if not redis_client:
        return True  # Allow if Redis unavailable

    try:
        key = get_rate_limit_key(wa_id)
        current = redis_client.get(key)

        if current is None:
            # First message in window
            redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
            return True

        count = int(current)
        if count >= MAX_MESSAGES_PER_WINDOW:
            logger.warning(f"Rate limit exceeded for {wa_id}")
            return False

        # Increment and extend TTL
        redis_client.incr(key)
        redis_client.expire(key, RATE_LIMIT_WINDOW)
        return True

    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error


async def send_message_with_retry(
    wa_id: str,
    text: str,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
) -> bool:
    """
    Send a message with exponential backoff retry on 429/5xx.
    """

    # Check rate limit first
    if not await check_rate_limit(wa_id):
        logger.warning(f"Message to {wa_id} throttled (rate limit)")
        return False

    backoff = initial_backoff

    for attempt in range(max_retries):
        try:
            response = await whatsapp_client.send_text_message(wa_id, text)

            # Check for errors
            if "error" in response:
                error_code = response.get("error", {}).get("code")

                # Retry on rate limit (429) or server errors (5xx)
                if error_code in [429, 500, 502, 503]:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Error {error_code} sending to {wa_id}. "
                            f"Retrying in {backoff}s (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(backoff)
                        backoff *= 2  # Exponential backoff
                        continue

                logger.error(f"Failed to send message to {wa_id}: {response}")
                return False

            logger.info(f"Message sent to {wa_id}")
            return True

        except Exception as e:
            logger.error(f"Exception sending message to {wa_id}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff)
                backoff *= 2

    logger.error(f"Failed to send message to {wa_id} after {max_retries} retries")
    return False


async def bulk_send_messages(
    recipients: list,
    text: str,
    delay_seconds: float = 1.0,
) -> dict:
    """
    Send same message to multiple recipients with delay.
    Returns success/failure counts.
    """
    import asyncio

    success = 0
    failed = 0

    for wa_id in recipients:
        try:
            if await send_message_with_retry(wa_id, text):
                success += 1
            else:
                failed += 1

            # Add delay between messages to avoid rate limiting
            await asyncio.sleep(delay_seconds)
        except Exception as e:
            logger.error(f"Error in bulk send to {wa_id}: {e}")
            failed += 1

    return {
        "total": len(recipients),
        "success": success,
        "failed": failed,
    }


def get_rate_limit_status(wa_id: str) -> Optional[dict]:
    """Get current rate limit status for a user."""
    if not redis_client:
        return None

    try:
        key = get_rate_limit_key(wa_id)
        current = redis_client.get(key)
        ttl = redis_client.ttl(key)

        if current is None:
            return {"allowed": True, "messages_sent": 0, "reset_in_seconds": 0}

        count = int(current)
        return {
            "allowed": count < MAX_MESSAGES_PER_WINDOW,
            "messages_sent": count,
            "reset_in_seconds": max(0, ttl),
        }
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return None


def reset_rate_limit(wa_id: str) -> bool:
    """Reset rate limit for a user (admin only)."""
    if not redis_client:
        return False

    try:
        key = get_rate_limit_key(wa_id)
        redis_client.delete(key)
        logger.info(f"Reset rate limit for {wa_id}")
        return True
    except Exception as e:
        logger.error(f"Error resetting rate limit: {e}")
        return False
