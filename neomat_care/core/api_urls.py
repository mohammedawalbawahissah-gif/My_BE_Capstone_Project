from django.urls import path
from . import views


urlpatterns = [
    path("", views.api_home, name="api_home"),
    path("patients/", views.api_patients),
    path("referrals/", views.api_referrals),
]
