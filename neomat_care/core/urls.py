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

from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.patients, name='patients'),
    path('patients/add/', views.patient_add, name='patient_add'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
]