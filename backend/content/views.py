import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import FAQ, LANGS, BookingRequest, CalculatorOption, GalleryImage, PricingPackage, SiteSettings, Testimonial, TextBlock


def _lang(request):
    lang = request.GET.get("lang", "en")
    return lang if lang in LANGS else "en"


@require_GET
def site_content(request):
    """Everything the landing page needs, in one request."""
    lang = _lang(request)
    active = lambda m: m.objects.filter(is_active=True)  # noqa: E731
    cfg = SiteSettings.load()
    return JsonResponse({
        "settings": {
            "phone": cfg.phone, "whatsapp": cfg.whatsapp_number, "email": cfg.email,
            "instagram": cfg.instagram_url, "tiktok": cfg.tiktok_url, "facebook": cfg.facebook_url,
            "areas": [a.strip() for a in cfg.service_areas.split(",") if a.strip()],
            "happyCustomers": cfg.happy_customers, "startingPrice": cfg.starting_price_eur,
            "hourlyRate": cfg.hourly_rate_eur,
        },
        # Only non-empty overrides; the frontend falls back to its bundled translations.
        "texts": {b.key: v for b in TextBlock.objects.all() if (v := getattr(b, f"value_{lang}"))},
        "packages": [
            {"id": p.id, "name": p.tr("name", lang), "description": p.tr("description", lang),
             "price": p.price_eur, "hours": p.estimated_hours,
             "referralBonus": p.referral_bonus_eur, "popular": p.is_popular}
            for p in active(PricingPackage)
        ],
        "calculator": [
            {"id": o.id, "label": o.tr("label", lang), "price": o.price_eur, "hourly": o.is_hourly}
            for o in active(CalculatorOption)
        ],
        "testimonials": [
            {"id": t.id, "author": t.author, "city": t.city, "quote": t.tr("quote", lang),
             "photo": t.photo.url if t.photo else ""}
            for t in active(Testimonial)
        ],
        "faq": [{"id": f.id, "q": f.tr("question", lang), "a": f.tr("answer", lang)} for f in active(FAQ)],
        "gallery": [{"id": g.id, "src": g.src, "caption": g.caption} for g in active(GalleryImage)],
    })


@csrf_exempt
@require_POST
def create_booking(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)
    missing = [f for f in ("name", "phone", "furniture") if not str(data.get(f, "")).strip()]
    if missing:
        return JsonResponse({"error": "missing fields", "fields": missing}, status=400)
    booking = BookingRequest.objects.create(
        name=data["name"][:100], phone=data["phone"][:30], city=data.get("city", "")[:50],
        furniture=data["furniture"], preferred_date=data.get("preferred_date") or None,
        language=data.get("language", "en")[:2],
    )
    return JsonResponse({"id": booking.id}, status=201)
