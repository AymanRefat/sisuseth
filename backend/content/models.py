from django.db import models

LANGS = ("en", "fi", "sv")


def tr_fields(field_cls, **kwargs):
    """Return one field per supported language: {name_en, name_fi, name_sv}."""
    return {lang: field_cls(blank=(lang != "en"), **kwargs) for lang in LANGS}


class Translatable(models.Model):
    """Base with a helper to read a field in the requested language (fallback: English)."""

    class Meta:
        abstract = True

    def tr(self, field, lang):
        value = getattr(self, f"{field}_{lang}", "") if lang in LANGS else ""
        return value or getattr(self, f"{field}_en")


def _add(cls, name, field_cls, **kwargs):
    for lang, f in tr_fields(field_cls, **kwargs).items():
        cls.add_to_class(f"{name}_{lang}", f)


class Ordered(models.Model):
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class PricingPackage(Translatable, Ordered):
    price_eur = models.PositiveIntegerField()
    estimated_hours = models.PositiveSmallIntegerField(default=1)
    referral_bonus_eur = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name_en


_add(PricingPackage, "name", models.CharField, max_length=100)
_add(PricingPackage, "description", models.CharField, max_length=200)


class CalculatorOption(Translatable, Ordered):
    price_eur = models.PositiveIntegerField()
    is_hourly = models.BooleanField(default=False)

    def __str__(self):
        return self.label_en


_add(CalculatorOption, "label", models.CharField, max_length=150)


class Testimonial(Translatable, Ordered):
    author = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="testimonials/", blank=True)

    def __str__(self):
        return f"{self.author} ({self.city})"


_add(Testimonial, "quote", models.TextField)


class FAQ(Translatable, Ordered):
    def __str__(self):
        return self.question_en


_add(FAQ, "question", models.CharField, max_length=200)
_add(FAQ, "answer", models.TextField)


class GalleryImage(Ordered):
    image = models.ImageField(upload_to="gallery/", blank=True)
    image_url = models.URLField(blank=True, help_text="Used when no file is uploaded")
    caption = models.CharField(max_length=150, blank=True)

    @property
    def src(self):
        return self.image.url if self.image else self.image_url

    def __str__(self):
        return self.caption or self.src


class BookingRequest(models.Model):
    STATUS = [("new", "New"), ("contacted", "Contacted"), ("done", "Done")]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    city = models.CharField(max_length=50, blank=True)
    furniture = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=2, default="en")
    status = models.CharField(max_length=10, choices=STATUS, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} – {self.created_at:%Y-%m-%d}"


class SiteSettings(models.Model):
    """Single row holding contact data and global numbers shown on the site."""

    phone = models.CharField(max_length=30, default="+358 40 871 3636")
    whatsapp_number = models.CharField(max_length=20, default="358408713636", help_text="Digits only, with country code")
    email = models.EmailField(default="info@sisuseth.com")
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    service_areas = models.CharField(max_length=200, default="Helsinki, Espoo, Vantaa", help_text="Comma separated")
    happy_customers = models.PositiveIntegerField(default=500)
    starting_price_eur = models.PositiveIntegerField(default=50)
    hourly_rate_eur = models.PositiveIntegerField(default=40)

    class Meta:
        verbose_name = verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]


class TextBlock(Translatable):
    """Overrides a UI text key (e.g. "hero.title"). Empty = React default is used."""

    key = models.CharField(max_length=100, unique=True)
    note = models.CharField(max_length=200, blank=True, help_text="Where this text appears")

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key


_add(TextBlock, "value", models.TextField)
