from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_migrate


def seed_after_migrate(sender, using, verbosity=1, **kwargs):
    """Load the starting content ONCE: on the first `migrate` of an empty database.

    Runs after ALL migrations, so it always matches the current models. On every later migrate/deploy
    the database already has its SiteSettings row, so this does nothing (one quick query).
    To add starting content or new text keys to an existing database, run `manage.py seed` by hand.
    Set SEED_ON_MIGRATE=0 to skip completely (the tests do).
    """
    from .models import SiteSettings

    if getattr(settings, "SEED_ON_MIGRATE", True) and not SiteSettings.objects.using(using).exists():
        call_command("seed", verbosity=verbosity)


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'

    def ready(self):
        post_migrate.connect(seed_after_migrate, sender=self, dispatch_uid="content-seed-after-migrate")
