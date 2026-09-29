from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from content.models import BeforeAfter, GalleryImage, SiteSettings

pytestmark = pytest.mark.usefixtures("seeded")

ADMIN_MODELS = ["sitesettings", "textblock", "pricingpackage", "calculatoroption", "testimonial", "faq",
                "galleryimage", "product", "beforeafter", "video", "bookingrequest", "painpoint", "step", "timelineentry"]


def jpeg(size):
    buf = BytesIO()
    Image.new("RGB", size, "orange").save(buf, "JPEG")
    return SimpleUploadedFile("photo.jpg", buf.getvalue(), content_type="image/jpeg")


@pytest.mark.parametrize("model", ADMIN_MODELS)
def test_admin_pages_load(admin_client, model):
    assert admin_client.get(reverse(f"admin:content_{model}_changelist")).status_code == 200
    assert admin_client.get(reverse(f"admin:content_{model}_add")).status_code in (200, 403)


def test_site_settings_page_shows_feature_switches(admin_client):
    html = admin_client.get(reverse("admin:content_sitesettings_change", args=[1])).content.decode()
    assert "Features – turn website sections on/off" in html and "feature_quiz" in html


def test_site_settings_is_single_row():
    SiteSettings(phone="1").save()
    assert SiteSettings.objects.count() == 1


def test_admin_requires_login(client):
    assert client.get("/admin/").status_code == 302


def test_large_uploads_are_resized():
    photo = GalleryImage(image=jpeg((4000, 3000)))
    photo.save()
    assert max(Image.open(photo.image.path).size) == 1600


def test_small_uploads_untouched():
    photo = GalleryImage(image=jpeg((800, 600)))
    photo.save()
    assert Image.open(photo.image.path).size == (800, 600)


def test_before_after_in_api(content):
    BeforeAfter.objects.create(before=jpeg((10, 10)), after=jpeg((10, 10)), caption_en="Kitchen", caption_fi="Keittiö")
    assert content()["beforeAfter"][0]["caption"] == "Keittiö"
