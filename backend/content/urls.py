from django.urls import path

from . import views

urlpatterns = [
    path("content/", views.site_content),
    path("gallery/", views.GalleryList.as_view()),
    path("bookings/", views.BookingCreate.as_view()),
]
