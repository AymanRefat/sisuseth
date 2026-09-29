from unittest import mock

import pytest

from content.models import BookingRequest, Referral

pytestmark = pytest.mark.usefixtures("seeded")


@mock.patch("content.views.notify_telegram")
def test_booking(notify, post):
    res = post("/api/bookings/", {"name": "Test", "phone": "040123", "furniture": "PAX",
                                  "preferred_date": "2026-10-03", "language": "sv", "referral_code": " abc123 "})
    assert res.status_code == 201
    booking = BookingRequest.objects.get()
    assert (booking.language, booking.referral_code, str(booking.preferred_date)) == ("sv", "ABC123", "2026-10-03")
    notify.assert_called_once_with(booking)


@pytest.mark.parametrize("body, bad_field", [
    ({"name": "T"}, "phone"),
    ({"name": "T", "phone": "1", "furniture": "x", "preferred_date": "tomorrow"}, "preferred_date"),
    ({"name": "T", "phone": "1", "furniture": "x", "language": "de"}, "language"),
])
def test_booking_validation(post, body, bad_field):
    res = post("/api/bookings/", body)
    assert res.status_code == 400 and bad_field in res.json()
    assert not BookingRequest.objects.exists()


def test_forms_are_throttled(post):
    codes = [post("/api/bookings/", {"name": "T"}).status_code for _ in range(21)]
    assert codes[-1] == 429


def test_referral_same_phone_same_code(post, client):
    body = {"name": "Mika", "phone": "+358 40 123 4567"}
    first = post("/api/referrals/", body).json()["code"]
    assert post("/api/referrals/", body).json()["code"] == first
    assert first.startswith("MIKA") and Referral.objects.count() == 1
    assert client.get(f"/api/referrals/{first.lower()}/").json() == {"valid": True}
    assert client.get("/api/referrals/NOPE1/").json() == {"valid": False}


def test_referral_bad_phone(post):
    assert post("/api/referrals/", {"name": "A", "phone": "12"}).status_code == 400


def test_deactivated_referral_invalid(post, client):
    code = post("/api/referrals/", {"name": "Anna", "phone": "0401234567"}).json()["code"]
    Referral.objects.update(is_active=False)
    assert client.get(f"/api/referrals/{code}/").json() == {"valid": False}


def test_referrals_disabled(post, client, site):
    code = post("/api/referrals/", {"name": "Anna", "phone": "0401234567"}).json()["code"]
    site(feature_referrals=False)
    assert post("/api/referrals/", {"name": "B", "phone": "0409999999"}).status_code == 404
    assert client.get(f"/api/referrals/{code}/").json() == {"valid": False}
