from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Web app
    path("", include("core.urls")),

    # REST API
    path("api/", include("core.api_urls")),
]