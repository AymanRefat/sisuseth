from django.urls import path

from . import views

urlpatterns = [
    path("content/", views.site_content),
    path("bookings/", views.BookingCreate.as_view()),
    path("google-reviews/", views.google_reviews),
    path("referrals/", views.create_referral),
    path("referrals/<str:code>/", views.check_referral),
]
