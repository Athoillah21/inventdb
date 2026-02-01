import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_approval_request(user):
    """
    Sends a message to the configured Telegram chat when a new user registers.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not token or not chat_id:
        print("DEBUG: Telegram settings missing!")
        logger.warning("Telegram settings not configured. Skipping notification.")
        return

    print(f"DEBUG: Sending to Telegram... Token={token[:5]}... ChatID={chat_id}") # DEBUG


    message = (
        f"🆕 *New User Registration*\n\n"
        f"👤 *Username*: {user.username}\n"
        f"📧 *Email*: {user.email}\n"
        f"📅 *Date*: {user.date_joined.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"⚠️ Account is inactive pending approval.\n"
        f"Please log in to the admin panel to activate."
    )

    # Create Inline Keyboard
    import json
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve_{user.id}"},
                {"text": "❌ Deny", "callback_data": f"deny_{user.id}"}
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(reply_markup)
    }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"DEBUG: Telegram Response: {response.status_code} - {response.text}")
        response.raise_for_status()
        logger.info(f"Telegram notification sent for user {user.username}")
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
