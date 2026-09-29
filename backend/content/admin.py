from django.contrib import admin
from django.utils.html import format_html

from .models import (
    FAQ, BookingRequest, CalculatorOption, GalleryImage, PricingPackage, SiteSettings, Testimonial, TextBlock,
)

admin.site.site_header = "SISUSETH – Website dashboard"
admin.site.site_title = "SISUSETH CMS"
admin.site.index_title = "Manage website content"



@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("thumb", "caption", "order", "is_active")
    list_editable = ("caption", "order", "is_active")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:80px;border-radius:6px">', obj.image.url) if obj.image else "–"


for model in (PricingPackage, CalculatorOption, Testimonial, FAQ):
    admin.site.register(model, list_display=("__str__", "order", "is_active"), list_editable=("order", "is_active"))


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Contact", {"fields": ["phone", "whatsapp_number", "telegram_username", "email"]}),
        ("Social media", {"fields": ["instagram_url", "tiktok_url", "facebook_url"]}),
        ("Images", {"fields": ["logo", "hero_image"]}),
        ("Prices & numbers", {"fields": ["starting_price_eur", "hourly_rate_eur", "additional_item_eur", "happy_customers"]}),
        ("Lists", {"fields": ["service_areas", "brands"]}),
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
    list_editable = ("status",)
