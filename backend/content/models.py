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


# On/off switches for optional website features. Each becomes a checkbox in the CMS
# (Site settings → Features) and is sent to the frontend as settings.features.<key>.
# Keep in sync with docs/FEATURES.md.
FEATURES = [
    # (key, label, default)
    ("product_search", "Product price search (e.g. 'PAX' → price)", True),
    ("mobile_bar", "Sticky booking bar on phones", True),
    ("before_after", "Before/after photo slider", True),
    ("videos", "Video strip (short clips)", True),
    ("hours_counter", "'Weekend hours saved' counter", True),
    ("timeline_animation", "Animated DIY vs SISUSETH timeline", True),
    ("quiz", "'How long would it take you?' quiz", True),
    ("hero_animation", "Flat-pack box animation in the hero", True),
    ("tax_credit", "Household tax credit (kotitalousvähennys) calculator", True),
]


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

    # Hours counter: shown number = base + completed bookings × hours per job
    hours_saved_base = models.PositiveIntegerField(default=1000, help_text="Hours saved before bookings were tracked here")
    hours_per_job = models.DecimalField(max_digits=4, decimal_places=1, default=3, help_text="Weekend hours saved per completed booking")

    # Quiz: DIY time = our assembly time × multiplier
    quiz_beginner_multiplier = models.DecimalField(max_digits=3, decimal_places=1, default=4)
    quiz_average_multiplier = models.DecimalField(max_digits=3, decimal_places=1, default=2.5)
    quiz_handy_multiplier = models.DecimalField(max_digits=3, decimal_places=1, default=1.5)

    # Kotitalousvähennys (Finnish household tax credit). Check vero.fi every year.
    tax_credit_rate_percent = models.PositiveSmallIntegerField(default=35)
    tax_credit_labour_percent = models.PositiveSmallIntegerField(default=100, help_text="Share of the price that is labour")
    tax_credit_deductible_eur = models.PositiveIntegerField(default=150, help_text="Yearly own-liability per person")
    tax_credit_max_eur = models.PositiveIntegerField(default=1600, help_text="Yearly maximum per person")

    # Sections whose starting content was already loaded by `seed`. Once loaded, a section is never
    # re-filled, so anything the owner deletes stays deleted after future deploys.
    seeded_sections = models.JSONField(default=list, blank=True, editable=False)

    class Meta:
        verbose_name = verbose_name_plural = "Site settings"

    @property
    def features(self):
        return {key: getattr(self, f"feature_{key}") for key, _, _ in FEATURES}

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


for _key, _label, _default in FEATURES:
    SiteSettings.add_to_class(f"feature_{_key}", models.BooleanField(_label, default=_default))


class Product(Ordered):
    """Searchable product with a fixed assembly estimate (feature: product_search, quiz)."""

    name = models.CharField(max_length=100, help_text="e.g. PAX wardrobe 100×58×236")
    brand = models.CharField(max_length=50, default="IKEA")
    price_eur = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField(help_text="Our typical assembly time")

    class Meta(Ordered.Meta):
        ordering = ["brand", "name"]

    def __str__(self):
        return f"{self.brand} {self.name}"


class BeforeAfter(Translatable, Ordered):
    before = models.ImageField(upload_to="before_after/")
    after = models.ImageField(upload_to="before_after/")

    class Meta(Ordered.Meta):
        verbose_name = verbose_name_plural = "Before/after photos"

    def save(self, *args, **kwargs):
        shrink_image(self.before)
        shrink_image(self.after)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption_en or f"Before/after #{self.pk}"


_add(BeforeAfter, "caption", models.CharField, max_length=150)
for _lang in LANGS:  # captions are optional
    BeforeAfter._meta.get_field(f"caption_{_lang}").blank = True


class Video(Translatable, Ordered):
    file = models.FileField(upload_to="videos/", help_text="Short MP4, ideally under 10 MB")
    poster = models.ImageField(upload_to="videos/", blank=True, help_text="Optional still image shown while loading")

    def save(self, *args, **kwargs):
        shrink_image(self.poster, 800)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption_en or self.file.name


_add(Video, "caption", models.CharField, max_length=150)
for _lang in LANGS:
    Video._meta.get_field(f"caption_{_lang}").blank = True


class PainPoint(Translatable, Ordered):
    """'Select your assembly frustrations' cards."""

    icon = models.CharField(max_length=8, blank=True, help_text="Optional emoji, e.g. 🔧")

    class Meta(Ordered.Meta):
        verbose_name = "Frustration card"

    def __str__(self):
        return self.title_en


_add(PainPoint, "title", models.CharField, max_length=100)
_add(PainPoint, "text", models.CharField, max_length=200)


class Step(Translatable, Ordered):
    """'How it works' steps. Numbered automatically in display order."""

    def __str__(self):
        return self.title_en


_add(Step, "title", models.CharField, max_length=100)
_add(Step, "text", models.CharField, max_length=250)


class TimelineEntry(Translatable, Ordered):
    """One row of the 'Your weekend: DIY vs SISUSETH' comparison."""

    SIDES = [("diy", "DIY weekend"), ("us", "SISUSETH weekend")]
    side = models.CharField(max_length=3, choices=SIDES)
    time = models.CharField(max_length=10, help_text="e.g. 10:30")

    class Meta(Ordered.Meta):
        verbose_name = "Weekend timeline row"
        verbose_name_plural = "Weekend timeline rows"
        ordering = ["side", "order", "id"]

    def __str__(self):
        return f"{self.get_side_display()} {self.time} – {self.text_en}"


_add(TimelineEntry, "text", models.CharField, max_length=200)


class TextBlock(Translatable):
    """Overrides a UI text key (e.g. "hero.title"). Empty = React default is used."""

    key = models.CharField(max_length=100, unique=True)
    note = models.CharField(max_length=200, blank=True, help_text="Where this text appears")

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key


_add(TextBlock, "value", models.TextField)
