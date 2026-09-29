"""Calls to outside services. Failures are logged and never break the customer's request."""
import json
import logging
import os
import secrets
import urllib.request

from django.core.cache import cache

from .models import Referral

logger = logging.getLogger(__name__)
GOOGLE_CACHE_SECONDS = 6 * 60 * 60


def _post_json(url, payload, headers=None, timeout=5):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout)


def notify_telegram(booking):
    """Send a new booking request to the owner's Telegram chat (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)."""
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return
    text = (f"🛠 New booking request\n\n👤 {booking.name}\n📞 {booking.phone}\n📍 {booking.city or '-'}\n"
            f"📅 {booking.preferred_date or '-'}\n🌐 {booking.language.upper()}\n"
            f"🎁 {booking.referral_code or '-'}\n\n{booking.furniture}")
    try:
        _post_json(f"https://api.telegram.org/bot{token}/sendMessage", {"chat_id": chat_id, "text": text})
    except Exception:
        logger.exception("Telegram notification failed")


def fetch_google_reviews(place_id, lang):
    """Rating + latest reviews from Google Places API (New), cached for 6 hours. None if unavailable."""
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not (api_key and place_id):
        return None
    cache_key = f"google-reviews:{place_id}:{lang}"
    if (cached := cache.get(cache_key)) is not None:
        return cached
    req = urllib.request.Request(
        f"https://places.googleapis.com/v1/places/{place_id}?languageCode={lang}",
        headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": "rating,userRatingCount,reviews,googleMapsUri"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as res:
            place = json.load(res)
    except Exception:
        logger.exception("Google reviews request failed")
        return None
    data = {
        "enabled": True,
        "rating": place.get("rating"),
        "count": place.get("userRatingCount", 0),
        "url": place.get("googleMapsUri", ""),
        "reviews": [
            {"author": r.get("authorAttribution", {}).get("displayName", ""),
             "photo": r.get("authorAttribution", {}).get("photoUri", ""),
             "rating": r.get("rating", 5),
             "text": (r.get("text") or r.get("originalText") or {}).get("text", ""),
             "when": r.get("relativePublishTimeDescription", "")}
            for r in place.get("reviews", [])
        ],
    }
    cache.set(cache_key, data, GOOGLE_CACHE_SECONDS)
    return data


def new_referral_code(name):
    prefix = "".join(c for c in name.upper() if c.isalpha())[:5] or "SISU"
    while True:
        code = f"{prefix}{secrets.randbelow(900) + 100}"
        if not Referral.objects.filter(code=code).exists():
            return code
