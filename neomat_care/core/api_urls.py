from django.urls import path
from . import views

urlpatterns = [
    path("", views.api_home, name="api_home"),
    path("patients/", views.api_patients, name="api_patients"),
    path("patients/create/", views.PatientListCreateAPIView.as_view(), name="api_patient_create"),
    path("register/", views.RegisterUserAPIView.as_view(), name="api_register_user"),
    path("referrals/", views.api_referrals, name="api_referrals"),
    path("referrals/create/", views.ReferralCreateAPIView.as_view(), name="api_referral_create"),
]
