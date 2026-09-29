from django.contrib import admin

from .models import (
    FAQ, BookingRequest, CalculatorOption, GalleryImage, PricingPackage, SiteSettings, Testimonial, TextBlock,
)

admin.site.site_header = "SISUSETH – Website dashboard"
admin.site.site_title = "SISUSETH CMS"
admin.site.index_title = "Manage website content"

for model in (PricingPackage, CalculatorOption, Testimonial, FAQ, GalleryImage):
    admin.site.register(model, list_display=("__str__", "order", "is_active"), list_editable=("order", "is_active"))


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Contact", {"fields": ["phone", "whatsapp_number", "email"]}),
        ("Social media", {"fields": ["instagram_url", "tiktok_url", "facebook_url"]}),
        ("Numbers shown on the site", {"fields": ["service_areas", "happy_customers", "starting_price_eur", "hourly_rate_eur"]}),
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
