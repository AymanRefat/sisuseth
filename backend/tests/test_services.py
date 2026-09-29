import io
import json
from unittest import mock

import pytest

from content import services
from content.models import BookingRequest

pytestmark = pytest.mark.usefixtures("seeded")

PLACE = {
    "rating": 4.87, "userRatingCount": 42, "googleMapsUri": "https://maps.google.com/?cid=1",
    "reviews": [{"rating": 5, "text": {"text": "Loistava!"}, "relativePublishTimeDescription": "viikko sitten",
                 "authorAttribution": {"displayName": "Liisa", "photoUri": "https://x/p.jpg"}}],
}


def fake_response(payload):
    res = io.BytesIO(json.dumps(payload).encode())
    res.__enter__, res.__exit__ = lambda *a: res, lambda *a: None
    return res


def test_telegram_skipped_without_env(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with mock.patch("urllib.request.urlopen") as urlopen:
        services.notify_telegram(BookingRequest(name="A", phone="1", furniture="x"))
    urlopen.assert_not_called()


def test_telegram_message(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    booking = BookingRequest(name="Anna", phone="040", furniture="PAX", referral_code="MIKA123")
    with mock.patch("urllib.request.urlopen") as urlopen:
        services.notify_telegram(booking)
    req = urlopen.call_args.args[0]
    assert req.full_url == "https://api.telegram.org/botTOKEN/sendMessage"
    body = json.loads(req.data)
    assert body["chat_id"] == "42" and "Anna" in body["text"] and "MIKA123" in body["text"]


def test_telegram_failure_does_not_break_booking(monkeypatch, post):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    with mock.patch("urllib.request.urlopen", side_effect=OSError("down")):
        assert post("/api/bookings/", {"name": "A", "phone": "1", "furniture": "x"}).status_code == 201


def test_google_reviews_off_by_default(client):
    assert client.get("/api/google-reviews/").json() == {"enabled": False}


def test_google_reviews_fetched_and_cached(monkeypatch, client, site):
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "KEY")
    site(feature_google_reviews=True, google_place_id="PLACE1")
    with mock.patch("urllib.request.urlopen", return_value=fake_response(PLACE)) as urlopen:
        first = client.get("/api/google-reviews/?lang=fi").json()
        second = client.get("/api/google-reviews/?lang=fi").json()
    assert urlopen.call_count == 1  # second call served from cache
    assert first == second
    assert first["rating"] == 4.87 and first["count"] == 42
    assert first["reviews"][0] == {"author": "Liisa", "photo": "https://x/p.jpg", "rating": 5,
                                   "text": "Loistava!", "when": "viikko sitten"}
    req = urlopen.call_args.args[0]
    assert "places/PLACE1?languageCode=fi" in req.full_url and req.get_header("X-goog-api-key") == "KEY"


def test_google_reviews_error_hides_section(monkeypatch, client, site):
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "KEY")
    site(feature_google_reviews=True, google_place_id="PLACE1")
    with mock.patch("urllib.request.urlopen", side_effect=OSError("quota")):
        assert client.get("/api/google-reviews/").json() == {"enabled": False}


def test_referral_code_format():
    code = services.new_referral_code("Äkkinen Pekka")
    assert code[:5] == "ÄKKIN" and code[5:].isdigit() and len(code) == 8
    assert services.new_referral_code("123").startswith("SISU")
