from rest_framework import generics
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import EmergencyCase
from core.services.referral_engine import generate_referral
from core.serializers import HealthFacilitySerializer, TransportSerializer


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RegisterUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny] 

class SuggestReferralView(APIView):
    """
    Suggests the best facility and transport for a given emergency case.
    """

    def post(self, request):
        case_id = request.data.get("emergency_case_id")
        latitude = request.data.get("current_latitude")
        longitude = request.data.get("current_longitude")

        # Basic validation
        if not all([case_id, latitude, longitude]):
            return Response({"error": "emergency_case_id, current_latitude, current_longitude are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            case = EmergencyCase.objects.get(id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Emergency case not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # Call the referral engine
        result = generate_referral(case, latitude, longitude)

        if not result["facility"]:
            return Response({"error": "No suitable facility found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the results
        facility_data = HealthFacilitySerializer(result["facility"]).data
        transport_data = TransportSerializer(result["transport"][0]).data if result["transport"] else None

        return Response({
            "priority": result["priority"],
            "recommended_facility": facility_data,
            "transport": transport_data
        }, status=status.HTTP_200_OK)
