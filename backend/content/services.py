"""Calls to outside services. Failures are logged and never break the customer's request."""
import json
import logging
import os
import urllib.request

logger = logging.getLogger(__name__)


def notify_telegram(booking):
    """Send a new booking request to the owner's Telegram chat (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)."""
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return
    text = (f"🛠 New booking request\n\n👤 {booking.name}\n📞 {booking.phone}\n📍 {booking.city or '-'}\n"
            f"📅 {booking.preferred_date or '-'}\n🌐 {booking.language.upper()}\n\n{booking.furniture}")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        logger.exception("Telegram notification failed")
