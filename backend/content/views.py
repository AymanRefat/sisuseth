from rest_framework import generics, status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from . import serializers as s
from .models import (
    FAQ, LANGS, BeforeAfter, CalculatorOption, GalleryImage, PricingPackage, Product, Referral, SiteSettings,
    Testimonial, TextBlock, Video,
)
from .services import fetch_google_reviews, new_referral_code, notify_telegram


def get_lang(request):
    lang = request.query_params.get("lang", "fi")
    return lang if lang in LANGS else "fi"


class FormThrottle(AnonRateThrottle):
    """Limits spam on the public forms."""
    rate = "20/hour"


# Sections of the page: (response key, model, serializer). Only active rows are returned.
SECTIONS = [
    ("packages", PricingPackage, s.PricingPackageSerializer),
    ("calculator", CalculatorOption, s.CalculatorOptionSerializer),
    ("testimonials", Testimonial, s.TestimonialSerializer),
    ("faq", FAQ, s.FAQSerializer),
    ("gallery", GalleryImage, s.GalleryImageSerializer),
    ("products", Product, s.ProductSerializer),
    ("beforeAfter", BeforeAfter, s.BeforeAfterSerializer),
    ("videos", Video, s.VideoSerializer),
]


@api_view(["GET"])
def site_content(request):
    """Everything the landing page needs, in one request."""
    lang = get_lang(request)
    ctx = {"lang": lang}
    data = {
        "settings": s.SiteSettingsSerializer(SiteSettings.load(), context=ctx).data,
        # Only non-empty overrides; the frontend falls back to its bundled translations.
        "texts": {b.key: v for b in TextBlock.objects.all() if (v := getattr(b, f"value_{lang}"))},
    }
    for key, model, serializer in SECTIONS:
        data[key] = serializer(model.objects.filter(is_active=True), many=True, context=ctx).data
    return Response(data)


class BookingCreate(generics.CreateAPIView):
    serializer_class = s.BookingRequestSerializer
    throttle_classes = [FormThrottle]

    def perform_create(self, serializer):
        notify_telegram(serializer.save())


@api_view(["GET"])
def google_reviews(request):
    cfg = SiteSettings.load()
    data = cfg.feature_google_reviews and fetch_google_reviews(cfg.google_place_id, get_lang(request))
    return Response(data or {"enabled": False})


@api_view(["POST"])
@throttle_classes([FormThrottle])
def create_referral(request):
    """Customer asks for their own referral code. The same phone number always gets the same code."""
    if not SiteSettings.load().feature_referrals:
        raise NotFound
    serializer = s.ReferralSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = serializer.validated_data["phone"]
    referral = Referral.objects.filter(phone=phone).first() or serializer.save(
        code=new_referral_code(serializer.validated_data["name"]))
    return Response({"code": referral.code}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def check_referral(request, code):
    valid = SiteSettings.load().feature_referrals and Referral.objects.filter(code=code.upper(), is_active=True).exists()
    return Response({"valid": valid})
