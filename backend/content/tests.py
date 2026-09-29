from unittest import mock

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

from .models import BookingRequest, Referral, SiteSettings


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", stdout=mock.MagicMock())

    def setUp(self):
        cache.clear()  # reset throttling between tests

    def test_content_defaults_to_finnish(self):
        data = self.client.get("/api/content/").json()
        self.assertEqual(data["texts"]["hero.title"], "Älä tuhlaa viikonloppuasi!")
        self.assertEqual(data["faq"][0]["q"], "Onko turvallista päästää vieraita kotiin?")
        self.assertEqual(len(data["gallery"]), 15)
        self.assertTrue(data["gallery"][0]["src"].startswith("/media/gallery/"))

    def test_content_in_swedish_and_english(self):
        self.assertEqual(self.client.get("/api/content/?lang=sv").json()["packages"][0]["name"], "Bas")
        self.assertEqual(self.client.get("/api/content/?lang=en").json()["packages"][0]["name"], "Basic")

    def test_feature_flags_follow_cms(self):
        cfg = SiteSettings.load()
        cfg.feature_quiz = False
        cfg.save()
        features = self.client.get("/api/content/").json()["settings"]["features"]
        self.assertFalse(features["quiz"])
        self.assertTrue(features["product_search"])
        self.assertFalse(features["google_reviews"])

    def test_hours_saved_counts_completed_bookings(self):
        before = self.client.get("/api/content/").json()["settings"]["hoursSaved"]
        BookingRequest.objects.create(name="A", phone="1", furniture="x", status="done")
        after = self.client.get("/api/content/").json()["settings"]["hoursSaved"]
        self.assertEqual(after - before, 3)

    @mock.patch("content.views.notify_telegram")
    def test_booking(self, notify):
        res = self.client.post("/api/bookings/", {"name": "Test", "phone": "040123", "furniture": "PAX",
                                                  "referral_code": "abc123"}, content_type="application/json")
        self.assertEqual(res.status_code, 201)
        booking = BookingRequest.objects.get()
        self.assertEqual((booking.language, booking.referral_code), ("fi", "ABC123"))
        notify.assert_called_once_with(booking)

    def test_booking_requires_fields(self):
        res = self.client.post("/api/bookings/", {"name": "Test"}, content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("phone", res.json())

    def test_referral_same_phone_same_code(self):
        body = {"name": "Mika", "phone": "+358 40 123 4567"}
        first = self.client.post("/api/referrals/", body, content_type="application/json").json()["code"]
        second = self.client.post("/api/referrals/", body, content_type="application/json").json()["code"]
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("MIKA"))
        self.assertTrue(self.client.get(f"/api/referrals/{first.lower()}/").json()["valid"])
        self.assertFalse(self.client.get("/api/referrals/NOPE1/").json()["valid"])

    def test_referral_disabled(self):
        cfg = SiteSettings.load()
        cfg.feature_referrals = False
        cfg.save()
        res = self.client.post("/api/referrals/", {"name": "A", "phone": "0401234567"}, content_type="application/json")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(Referral.objects.count(), 0)

    def test_google_reviews_off_without_key(self):
        self.assertEqual(self.client.get("/api/google-reviews/").json(), {"enabled": False})
