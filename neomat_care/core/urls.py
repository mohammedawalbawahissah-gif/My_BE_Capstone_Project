from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("patients/", views.patients, name="patients"),
    path("referrals/", views.referrals, name="referrals"),
    path("emergency/", views.emergency, name="emergency"),
    path("facilities/", views.facilities, name="facilities"),
    path("transport/", views.transport, name="transport"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
]