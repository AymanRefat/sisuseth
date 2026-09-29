import json

import pytest
from django.conf import settings

from content.models import FEATURES, BookingRequest, FAQ, Product, TextBlock

pytestmark = pytest.mark.usefixtures("seeded")


def test_defaults_to_finnish(content):
    data = content()
    assert data["texts"]["hero.title"] == "Älä tuhlaa *viikonloppuasi*!"
    assert data["faq"][0]["q"] == "Onko turvallista päästää vieraita kotiin?"


@pytest.mark.parametrize("lang, name", [("fi", "Perus"), ("sv", "Bas"), ("en", "Basic"), ("de", "Perus")])
def test_languages_and_unknown_language_falls_back_to_finnish(content, lang, name):
    assert content(lang)["packages"][0]["name"] == name


def test_missing_translation_falls_back_to_english(content):
    faq = FAQ.objects.first()
    faq.question_sv = ""
    faq.save()
    assert content("sv")["faq"][0]["q"] == faq.question_en


def test_seeded_sections(content):
    data = content()
    assert data["galleryCount"] == 15
    assert len(data["products"]) == 18
    assert len(data["pains"]) == 6 and data["pains"][0] == {"id": data["pains"][0]["id"], "icon": "🔧",
                                                           "title": "Työkalut puuttuvat", "text": data["pains"][0]["text"]}
    assert [s["title"] for s in data["steps"]][0] == "Varaa WhatsAppilla"
    assert [(r["side"], r["time"]) for r in data["timeline"]][:2] == [("diy", "9:00"), ("diy", "10:30")]
    assert len([r for r in data["timeline"] if r["side"] == "us"]) == 5
    assert len(data["packages"]) == 3 and len(data["calculator"]) == 4 and len(data["faq"]) == 6
    assert data["beforeAfter"] == [] and data["videos"] == []
    assert data["settings"]["logo"] and data["settings"]["heroImage"]


def test_every_ui_text_is_editable_in_cms():
    keys = json.loads((settings.BASE_DIR.parent / "frontend/src/locales/en.json").read_text())
    assert set(TextBlock.objects.values_list("key", flat=True)) == set(keys)
    assert not TextBlock.objects.filter(value_fi="").exists()


def test_cms_text_override(content):
    TextBlock.objects.filter(key="hero.title").update(value_fi="Uusi otsikko")
    assert content()["texts"]["hero.title"] == "Uusi otsikko"


def test_inactive_items_hidden(content):
    Product.objects.filter(name__startswith="PAX").update(is_active=False)
    assert not [p for p in content()["products"] if p["name"].startswith("PAX")]


def test_all_feature_flags_exposed(content, site):
    features = content()["settings"]["features"]
    assert set(features) == {key for key, _, _ in FEATURES}
    assert all(features.values())
    site(feature_quiz=False)
    features = content()["settings"]["features"]
    assert features["quiz"] is False and features["videos"] is True


def test_settings_values(content, site):
    site(telegram_username="@sisu", service_areas="Helsinki, , Espoo", tax_credit_rate_percent=40)
    s = content()["settings"]
    assert s["telegram"] == "sisu"
    assert s["areas"] == ["Helsinki", "Espoo"]
    assert s["taxCredit"] == {"rate": 40, "labour": 100, "deductible": 150, "max": 1600}
    assert s["quiz"] == {"beginner": 4.0, "average": 2.5, "handy": 1.5}


def test_hours_saved_counts_only_done_bookings(content):
    base = content()["settings"]["hoursSaved"]
    BookingRequest.objects.create(name="A", phone="1", furniture="x", status="done")
    BookingRequest.objects.create(name="B", phone="1", furniture="x", status="new")
    assert content()["settings"]["hoursSaved"] == base + 3


def test_gallery_pages(client):
    first = client.get("/api/gallery/").json()
    assert first["count"] == 15 and len(first["results"]) == 9 and first["next"]
    second = client.get("/api/gallery/?page=2").json()
    assert len(second["results"]) == 6 and second["next"] is None
    assert first["results"][0]["src"].startswith("/media/gallery/")
    assert client.get("/api/gallery/?page=3").status_code == 404


def test_gallery_hides_inactive(client):
    from content.models import GalleryImage
    GalleryImage.objects.filter(order__lt=5).update(is_active=False)
    assert client.get("/api/gallery/").json()["count"] == 10
