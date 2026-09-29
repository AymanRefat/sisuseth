from unittest import mock

import pytest

from content.models import BookingRequest

pytestmark = pytest.mark.usefixtures("seeded")


@mock.patch("content.views.notify_telegram")
def test_booking(notify, post):
    res = post("/api/bookings/", {"name": "Test", "phone": "040123", "furniture": "PAX",
                                  "preferred_date": "2026-10-03", "language": "sv"})
    assert res.status_code == 201
    booking = BookingRequest.objects.get()
    assert (booking.language, str(booking.preferred_date)) == ("sv", "2026-10-03")
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
