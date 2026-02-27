from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add/", views.patient_add, name="patient_add"),
    path("<int:patient_id>/emergency/", views.create_emergency, name="create_emergency"),
    path("referrals/", views.referrals, name="referrals"),
    path("facilities/", views.facilities, name="facilities"),
    path("transport/", views.transport, name="transport"),
]