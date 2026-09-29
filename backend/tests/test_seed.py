"""The seed command runs on every deploy, so it must never undo the owner's changes."""
import pytest
from django.core.management import call_command

from content.models import FAQ, GalleryImage, PainPoint, SiteSettings, TextBlock

pytestmark = pytest.mark.usefixtures("seeded")


def seed(*args):
    call_command("seed", *args, stdout=open("/dev/null", "w"))


def test_deleted_content_stays_deleted():
    GalleryImage.objects.all().delete()
    PainPoint.objects.first().delete()
    seed()
    assert GalleryImage.objects.count() == 0
    assert PainPoint.objects.count() == 5


def test_edited_content_and_texts_are_kept():
    FAQ.objects.filter(order=0).update(question_fi="Oma kysymys")
    TextBlock.objects.filter(key="hero.title").update(value_fi="Oma otsikko")
    seed()
    assert FAQ.objects.get(order=0).question_fi == "Oma kysymys"
    assert TextBlock.objects.get(key="hero.title").value_fi == "Oma otsikko"


def test_all_sections_marked_as_seeded():
    assert set(SiteSettings.load().seeded_sections) == {
        "site_images", "packages", "calculator", "faq", "testimonials", "gallery", "products", "pains", "steps",
        "timeline"}


def test_owner_logo_not_replaced(tmp_path):
    cfg = SiteSettings.load()
    cfg.logo.name = "site/my-own-logo.png"
    cfg.seeded_sections = []
    cfg.save()
    seed()
    assert SiteSettings.load().logo.name == "site/my-own-logo.png"


def test_existing_content_is_never_mixed_with_starting_content():
    cfg = SiteSettings.load()
    cfg.seeded_sections = []  # e.g. a database from before seed tracking existed
    cfg.save()
    seed()
    assert GalleryImage.objects.count() == 15 and FAQ.objects.count() == 6


def test_reset_reloads_a_section():
    GalleryImage.objects.all().delete()
    seed("--reset", "gallery")
    assert GalleryImage.objects.count() == 15


def test_obsolete_text_keys_removed_and_new_ones_added():
    TextBlock.objects.create(key="old.removed.key", value_en="x")
    TextBlock.objects.filter(key="hero.title").delete()
    seed()
    assert not TextBlock.objects.filter(key="old.removed.key").exists()
    assert TextBlock.objects.filter(key="hero.title").exists()
