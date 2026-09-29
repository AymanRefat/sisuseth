from rest_framework import serializers

from .models import (
    FAQ, LANGS, BeforeAfter, BookingRequest, CalculatorOption, GalleryImage, PricingPackage, Product, Referral,
    SiteSettings, Testimonial, Video,
)


class TranslatedField(serializers.Field):
    """Reads `<field>_<lang>` using the language in the serializer context (fallback: English)."""

    def __init__(self, field, **kwargs):
        self.field = field
        super().__init__(source="*", read_only=True, **kwargs)

    def to_representation(self, obj):
        return obj.tr(self.field, self.context.get("lang", "fi"))


class FileUrlField(serializers.FileField):
    """Relative URL (/media/...) instead of DRF's absolute one, so it works behind any proxy."""

    def to_representation(self, value):
        return value.url if value else ""


class PricingPackageSerializer(serializers.ModelSerializer):
    name = TranslatedField("name")
    description = TranslatedField("description")
    price = serializers.IntegerField(source="price_eur")
    hours = serializers.IntegerField(source="estimated_hours")
    referralBonus = serializers.IntegerField(source="referral_bonus_eur")
    popular = serializers.BooleanField(source="is_popular")

    class Meta:
        model = PricingPackage
        fields = ["id", "name", "description", "price", "hours", "referralBonus", "popular"]


class CalculatorOptionSerializer(serializers.ModelSerializer):
    label = TranslatedField("label")
    price = serializers.IntegerField(source="price_eur")
    hourly = serializers.BooleanField(source="is_hourly")

    class Meta:
        model = CalculatorOption
        fields = ["id", "label", "price", "hourly"]


class TestimonialSerializer(serializers.ModelSerializer):
    quote = TranslatedField("quote")
    photo = FileUrlField()

    class Meta:
        model = Testimonial
        fields = ["id", "author", "city", "quote", "photo"]


class FAQSerializer(serializers.ModelSerializer):
    q = TranslatedField("question")
    a = TranslatedField("answer")

    class Meta:
        model = FAQ
        fields = ["id", "q", "a"]


class GalleryImageSerializer(serializers.ModelSerializer):
    src = FileUrlField(source="image")

    class Meta:
        model = GalleryImage
        fields = ["id", "src", "caption"]


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(source="price_eur")

    class Meta:
        model = Product
        fields = ["id", "name", "brand", "price", "minutes"]


class BeforeAfterSerializer(serializers.ModelSerializer):
    before = FileUrlField()
    after = FileUrlField()
    caption = TranslatedField("caption")

    class Meta:
        model = BeforeAfter
        fields = ["id", "before", "after", "caption"]


class VideoSerializer(serializers.ModelSerializer):
    src = FileUrlField(source="file")
    poster = FileUrlField()
    caption = TranslatedField("caption")

    class Meta:
        model = Video
        fields = ["id", "src", "poster", "caption"]


def _split(value):
    return [part.strip() for part in value.split(",") if part.strip()]


class SiteSettingsSerializer(serializers.ModelSerializer):
    whatsapp = serializers.CharField(source="whatsapp_number")
    telegram = serializers.SerializerMethodField()
    instagram = serializers.URLField(source="instagram_url")
    tiktok = serializers.URLField(source="tiktok_url")
    facebook = serializers.URLField(source="facebook_url")
    areas = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()
    happyCustomers = serializers.IntegerField(source="happy_customers")
    startingPrice = serializers.IntegerField(source="starting_price_eur")
    hourlyRate = serializers.IntegerField(source="hourly_rate_eur")
    additionalItem = serializers.IntegerField(source="additional_item_eur")
    logo = FileUrlField()
    heroImage = FileUrlField(source="hero_image")
    features = serializers.DictField(read_only=True)
    hoursSaved = serializers.SerializerMethodField()
    quiz = serializers.SerializerMethodField()
    taxCredit = serializers.SerializerMethodField()
    referralDiscount = serializers.IntegerField(source="referral_discount_eur")

    class Meta:
        model = SiteSettings
        fields = [
            "phone", "whatsapp", "telegram", "email", "instagram", "tiktok", "facebook", "areas", "brands",
            "happyCustomers", "startingPrice", "hourlyRate", "additionalItem", "logo", "heroImage", "features",
            "hoursSaved", "quiz", "taxCredit", "referralDiscount",
        ]

    def get_telegram(self, obj):
        return obj.telegram_username.lstrip("@")

    def get_areas(self, obj):
        return _split(obj.service_areas)

    def get_brands(self, obj):
        return _split(obj.brands)

    def get_hoursSaved(self, obj):
        done = BookingRequest.objects.filter(status="done").count()
        return obj.hours_saved_base + int(done * obj.hours_per_job)

    def get_quiz(self, obj):
        return {"beginner": float(obj.quiz_beginner_multiplier), "average": float(obj.quiz_average_multiplier),
                "handy": float(obj.quiz_handy_multiplier)}

    def get_taxCredit(self, obj):
        return {"rate": obj.tax_credit_rate_percent, "labour": obj.tax_credit_labour_percent,
                "deductible": obj.tax_credit_deductible_eur, "max": obj.tax_credit_max_eur}


class BookingRequestSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(choices=LANGS, default="fi")

    class Meta:
        model = BookingRequest
        fields = ["id", "name", "phone", "city", "furniture", "preferred_date", "language", "referral_code"]
        read_only_fields = ["id"]

    def validate_referral_code(self, value):
        return value.strip().upper()


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ["code", "name", "phone"]
        read_only_fields = ["code"]

    def validate_phone(self, value):
        if len([c for c in value if c.isdigit()]) < 6:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value.strip()
