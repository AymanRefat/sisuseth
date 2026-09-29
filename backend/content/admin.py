from django.contrib import admin
from django.utils.html import format_html

from .models import (
    FAQ, FEATURES, BeforeAfter, BookingRequest, CalculatorOption, GalleryImage, PainPoint, PricingPackage, Product, Step, TimelineEntry,
    SiteSettings, Testimonial, TextBlock, Video,
)

admin.site.site_header = "SISUSETH – Website dashboard"
admin.site.site_title = "SISUSETH CMS"
admin.site.index_title = "Manage website content"
admin.ModelAdmin.list_per_page = 25  # paginate every CMS list



@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("thumb", "caption", "order", "is_active")
    list_editable = ("caption", "order", "is_active")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:80px;border-radius:6px">', obj.image.url) if obj.image else "–"


for model in (PricingPackage, CalculatorOption, Testimonial, FAQ, PainPoint, Step):
    admin.site.register(model, list_display=("__str__", "order", "is_active"), list_editable=("order", "is_active"))


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Features – turn website sections on/off", {
            "fields": [f"feature_{key}" for key, _, _ in FEATURES],
            "description": "Details for each feature: docs/FEATURES.md in the code repository.",
        }),
        ("Contact", {"fields": ["phone", "whatsapp_number", "telegram_username", "email"]}),
        ("Social media", {"fields": ["instagram_url", "tiktok_url", "facebook_url"]}),
        ("Images", {"fields": ["logo", "hero_image"]}),
        ("Prices & numbers", {"fields": ["starting_price_eur", "hourly_rate_eur", "additional_item_eur", "happy_customers"]}),
        ("Lists", {"fields": ["service_areas", "brands"]}),
        ("Hours-saved counter", {"fields": ["hours_saved_base", "hours_per_job"],
                                 "description": "Shown number = base + completed bookings × hours per job."}),
        ("Quiz", {"fields": ["quiz_beginner_multiplier", "quiz_average_multiplier", "quiz_handy_multiplier"],
                  "description": "Customer's DIY time = our assembly time × multiplier."}),
        ("Household tax credit (kotitalousvähennys)", {
            "fields": ["tax_credit_rate_percent", "tax_credit_labour_percent", "tax_credit_deductible_eur", "tax_credit_max_eur"],
            "description": "Check the current rules on vero.fi every January and update these numbers.",
        }),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = ("key", "note", "value_en", "value_fi", "value_sv")
    search_fields = ("key", "note", "value_en", "value_fi", "value_sv")
    readonly_fields = ("key", "note")


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "preferred_date", "language", "status", "created_at")
    list_filter = ("status", "city", "language")
    search_fields = ("name", "phone")
    list_editable = ("status",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price_eur", "minutes", "is_active")
    list_editable = ("price_eur", "minutes", "is_active")
    list_filter = ("brand", "is_active")
    search_fields = ("name", "brand")


@admin.register(BeforeAfter)
class BeforeAfterAdmin(admin.ModelAdmin):
    list_display = ("preview", "caption_en", "order", "is_active")
    list_editable = ("order", "is_active")

    @admin.display(description="Preview")
    def preview(self, obj):
        return format_html('<img src="{}" style="height:60px"> → <img src="{}" style="height:60px">',
                           obj.before.url, obj.after.url)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ("side", "time", "text_en", "order", "is_active")
    list_editable = ("time", "order", "is_active")
    list_filter = ("side",)
