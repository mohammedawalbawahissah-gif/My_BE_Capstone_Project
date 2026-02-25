from django.urls import path
from .views import (
    RegisterUserAPIView,
    SuggestReferralView,
    CreateReferralView,
    AcceptReferralView,
    DispatchReferralView,
    CompleteReferralView,
    api_root,
)

urlpatterns = [
    path('', api_root, name="api-root"),
    path('register/', RegisterUserAPIView.as_view()),
    path('referrals/suggest/', SuggestReferralView.as_view()),
    path('referrals/create/', CreateReferralView.as_view()),
    path('referrals/<int:referral_id>/accept/', AcceptReferralView.as_view()),
    path('referrals/<int:referral_id>/dispatch/', DispatchReferralView.as_view()),
    path('referrals/<int:referral_id>/complete/', CompleteReferralView.as_view()),
]