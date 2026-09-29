from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageOps

MAX_IMAGE_PX = 1600

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


def shrink_image(field, max_px=MAX_IMAGE_PX):
    """Resize large uploads in place so the small server's disk and bandwidth stay cheap."""
    if not field or getattr(field, "_committed", True):
        return
    img = ImageOps.exif_transpose(Image.open(field))
    if max(img.size) <= max_px:
        field.seek(0)
        return
    img.thumbnail((max_px, max_px))
    fmt = "PNG" if img.mode in ("RGBA", "P") else "JPEG"
    buf = BytesIO()
    img.save(buf, fmt, quality=82, optimize=True)
    name = field.name.rsplit(".", 1)[0] + (".png" if fmt == "PNG" else ".jpg")
    field.save(name.rsplit("/", 1)[-1], ContentFile(buf.getvalue()), save=False)


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

    def save(self, *args, **kwargs):
        shrink_image(self.photo, 400)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.author} ({self.city})"


_add(Testimonial, "quote", models.TextField)


class FAQ(Translatable, Ordered):
    def __str__(self):
        return self.question_en


_add(FAQ, "question", models.CharField, max_length=200)
_add(FAQ, "answer", models.TextField)


class GalleryImage(Ordered):
    image = models.ImageField(upload_to="gallery/", help_text="Large photos are resized automatically")
    caption = models.CharField(max_length=150, blank=True)

    def save(self, *args, **kwargs):
        shrink_image(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or self.image.name


class BookingRequest(models.Model):
    STATUS = [("new", "New"), ("contacted", "Contacted"), ("done", "Done")]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    city = models.CharField(max_length=50, blank=True)
    furniture = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=2, default="fi")
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
    telegram_username = models.CharField(max_length=50, blank=True, help_text="Without @. Leave empty to hide Telegram buttons")
    email = models.EmailField(default="info@sisuseth.com")
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    service_areas = models.CharField(max_length=200, default="Helsinki, Espoo, Vantaa", help_text="Comma separated")
    happy_customers = models.PositiveIntegerField(default=500)
    starting_price_eur = models.PositiveIntegerField(default=50)
    hourly_rate_eur = models.PositiveIntegerField(default=40)
    additional_item_eur = models.PositiveIntegerField(default=45, help_text="Calculator: price per extra item")
    brands = models.CharField(max_length=300, default="IKEA, JYSK, Sotka, ISKU, Treetale, Kodin1", help_text="Comma separated")
    logo = models.ImageField(upload_to="site/", blank=True)
    hero_image = models.ImageField(upload_to="site/", blank=True, help_text="Big photo at the top of the page")

    class Meta:
        verbose_name = verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        shrink_image(self.logo, 600)
        shrink_image(self.hero_image)
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
