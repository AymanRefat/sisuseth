import json
from unittest import mock

import pytest

from content import services
from content.models import BookingRequest

pytestmark = pytest.mark.usefixtures("seeded")

def test_telegram_skipped_without_env(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with mock.patch("urllib.request.urlopen") as urlopen:
        services.notify_telegram(BookingRequest(name="A", phone="1", furniture="x"))
    urlopen.assert_not_called()


def test_telegram_message(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    booking = BookingRequest(name="Anna", phone="040", furniture="PAX")
    with mock.patch("urllib.request.urlopen") as urlopen:
        services.notify_telegram(booking)
    req = urlopen.call_args.args[0]
    assert req.full_url == "https://api.telegram.org/botTOKEN/sendMessage"
    body = json.loads(req.data)
    assert body["chat_id"] == "42" and "Anna" in body["text"]


def test_telegram_failure_does_not_break_booking(monkeypatch, post):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    with mock.patch("urllib.request.urlopen", side_effect=OSError("down")):
        assert post("/api/bookings/", {"name": "A", "phone": "1", "furniture": "x"}).status_code == 201
