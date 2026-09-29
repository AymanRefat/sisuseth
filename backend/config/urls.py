from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.png", permanent=True)),
    path("api/", include("content.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    # Everything else is the React app (built into frontend/dist).
    re_path(r"^(?!api/|admin/|static/|media/|favicon).*$", TemplateView.as_view(template_name="index.html")),
]
