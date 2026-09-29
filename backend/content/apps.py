from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_migrate


def seed_after_migrate(sender, using, verbosity=1, **kwargs):
    """`migrate` also loads the starting content (after ALL migrations, so it always matches the current models).

    Safe on every run: each section is loaded only once, so the owner's deletions and edits are kept.
    Set SEED_ON_MIGRATE=0 to skip (the tests do).
    """
    if getattr(settings, "SEED_ON_MIGRATE", True):
        call_command("seed", verbosity=verbosity)


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'

    def ready(self):
        post_migrate.connect(seed_after_migrate, sender=self, dispatch_uid="content-seed-after-migrate")
