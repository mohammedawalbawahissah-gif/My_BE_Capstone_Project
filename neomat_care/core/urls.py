from django.urls import path
from .views import (
    api_root,
    RegisterUserAPIView,
    SuggestReferralView,
    CreateReferralView,
    AcceptReferralView,
    DispatchReferralView,
    CompleteReferralView
)

urlpatterns = [
    path('', api_root),

    path('register/', RegisterUserAPIView.as_view()),
    path('referrals/suggest/', SuggestReferralView.as_view()),
    path('referrals/create/', CreateReferralView.as_view()),
    path('referrals/<int:referral_id>/accept/', AcceptReferralView.as_view()),
    path('referrals/<int:referral_id>/dispatch/', DispatchReferralView.as_view()),
    path('referrals/<int:referral_id>/complete/', CompleteReferralView.as_view()),
]

urlpatterns = [
    path("register/", views.register_user, name="register_user"),
    path("login/", views.login_user, name="login_user"),
    path("emergency/create/", views.create_emergency, name="create_emergency"),
    path("referral/create/", views.create_referral, name="create_referral"),
    path("transport/dispatch/", views.dispatch_transport, name="dispatch_transport"),
]