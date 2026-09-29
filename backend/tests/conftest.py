import pytest
from django.core.cache import cache
from django.core.management import call_command

from content.models import SiteSettings


@pytest.fixture(autouse=True)
def isolated(settings, tmp_path):
    """Uploads go to a temp folder, and throttling/Google caches start empty."""
    settings.MEDIA_ROOT = tmp_path / "media"
    cache.clear()


@pytest.fixture
def seeded(db):
    call_command("seed", stdout=open("/dev/null", "w"))


@pytest.fixture
def site(seeded):
    """Site settings, with a helper to change them: site(feature_quiz=False)."""
    def update(**fields):
        cfg = SiteSettings.load()
        for name, value in fields.items():
            setattr(cfg, name, value)
        cfg.save()
        return cfg
    return update


@pytest.fixture
def content(client):
    def get(lang=None):
        return client.get("/api/content/" + (f"?lang={lang}" if lang else "")).json()
    return get


@pytest.fixture
def post(client):
    def send(url, body):
        return client.post(url, body, content_type="application/json")
    return send
