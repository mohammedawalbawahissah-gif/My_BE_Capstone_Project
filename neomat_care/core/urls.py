from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUserAPIView
from .views import SuggestReferralView, CreateReferralView, AcceptReferralView, DispatchReferralView, CompleteReferralView


urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path("referrals/suggest/", SuggestReferralView.as_view(), name="suggest-referral"),
    path("referrals/create/", CreateReferralView.as_view(), name="create-referral"),
    path("referrals/<int:referral_id>/accept/", AcceptReferralView.as_view(), name="accept-referral"),
    path("referrals/<int:referral_id>/dispatch/", DispatchReferralView.as_view(), name="dispatch-referral"),
    path("referrals/<int:referral_id>/complete/", CompleteReferralView.as_view(), name="complete-referral"),
]
