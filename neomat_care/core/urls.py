from django.urls import path
from . import views

urlpatterns = [

    # Landing / Dashboard
    path("", views.home, name="home"),
    path("dashboard/", views.home, name="dashboard"),

    # Authentication
    path("login/", views.login_logout_view, name="login_logout"),
    path("register/", views.register_view, name="register"),

    # Patients
    path("patients/", views.patients, name="patients"),
    path("patients/add/", views.patient_add, name="patient_add"),
    path("patients/<int:patient_id>/edit/", views.patient_edit, name="patient_edit"),
    path("patients/<int:patient_id>/delete/", views.patient_delete, name="patient_delete"),
    path("patients/<int:patient_id>/emergency/", views.create_emergency, name="create_emergency"),

    # Referrals
    path("referrals/", views.referrals, name="referrals"),

    # Facilities
    path("facilities/", views.facilities, name="facilities"),

    # Transport
    path("transport/", views.transport, name="transport"),

    path("emergency/", views.emergency_view, name="emergency"),
]