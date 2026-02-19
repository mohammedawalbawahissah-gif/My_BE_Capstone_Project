from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUserAPIView
from .views import SuggestReferralView

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path("referrals/suggest/", SuggestReferralView.as_view(), name="suggest-referral"),
]
