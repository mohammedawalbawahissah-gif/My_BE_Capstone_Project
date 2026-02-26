from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # WEBSITE (HTML)
    path("", include("core.urls")),

    # API (JSON ONLY)
    path("api/", include("core.api_urls")),
]