import pytest

from content.models import FEATURES, BookingRequest, FAQ, Product, TextBlock

pytestmark = pytest.mark.usefixtures("seeded")


def test_defaults_to_finnish(content):
    data = content()
    assert data["texts"]["hero.title"] == "Älä tuhlaa viikonloppuasi!"
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
    assert len(data["gallery"]) == 15
    assert data["gallery"][0]["src"].startswith("/media/gallery/")
    assert len(data["products"]) == 18
    assert len(data["packages"]) == 3 and len(data["calculator"]) == 4 and len(data["faq"]) == 6
    assert data["beforeAfter"] == [] and data["videos"] == []
    assert data["settings"]["logo"] and data["settings"]["heroImage"]


def test_every_ui_text_is_editable_in_cms():
    assert TextBlock.objects.count() == 155
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
    assert features["google_reviews"] is False and features["quiz"] is True
    site(feature_quiz=False, feature_google_reviews=True)
    features = content()["settings"]["features"]
    assert features["quiz"] is False and features["google_reviews"] is True


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
