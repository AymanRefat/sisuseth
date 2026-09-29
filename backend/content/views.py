from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from . import serializers as s
from .models import (
    FAQ, LANGS, BeforeAfter, CalculatorOption, GalleryImage, PainPoint, PricingPackage, Product, SiteSettings, Step,
    Testimonial, TextBlock, TimelineEntry, Video,
)
from .services import notify_telegram


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
    ("pains", PainPoint, s.PainPointSerializer),
    ("steps", Step, s.StepSerializer),
    ("timeline", TimelineEntry, s.TimelineEntrySerializer),
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
    data["galleryCount"] = GalleryImage.objects.filter(is_active=True).count()
    return Response(data)


class GalleryPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 48


class GalleryList(generics.ListAPIView):
    """Gallery photos, 9 per page: /api/gallery/?page=2 → {count, next, previous, results}."""
    queryset = GalleryImage.objects.filter(is_active=True)
    serializer_class = s.GalleryImageSerializer
    pagination_class = GalleryPagination


class BookingCreate(generics.CreateAPIView):
    serializer_class = s.BookingRequestSerializer
    throttle_classes = [FormThrottle]

    def perform_create(self, serializer):
        notify_telegram(serializer.save())
