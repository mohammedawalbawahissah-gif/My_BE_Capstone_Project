from rest_framework import generics
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.services.referral_engine import generate_referral
from core.serializers import HealthFacilitySerializer, TransportSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Referral, EmergencyCase, HealthFacility, Transport
from core.serializers import ReferralSerializer


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

class CreateReferralView(APIView):
    """
    Create a referral for an emergency case to a receiving facility.
    """

    def post(self, request):
        emergency_case_id = request.data.get("emergency_case_id")
        receiving_facility_id = request.data.get("receiving_facility_id")

        if not all([emergency_case_id, receiving_facility_id]):
            return Response({"error": "emergency_case_id and receiving_facility_id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            case = EmergencyCase.objects.get(id=emergency_case_id)
            facility = HealthFacility.objects.get(id=receiving_facility_id)
        except (EmergencyCase.DoesNotExist, HealthFacility.DoesNotExist):
            return Response({"error": "Emergency case or facility not found"},
                            status=status.HTTP_404_NOT_FOUND)

        if facility.capacity <= 0:
            return Response({"error": "Receiving facility has no available capacity"},
                            status=status.HTTP_400_BAD_REQUEST)

        referral = Referral.objects.create(
            emergency_case=case,
            referring_facility=case.created_by.healthfacility_set.first(),
            receiving_facility=facility,
            status="PENDING"
        )

        return Response(ReferralSerializer(referral).data, status=status.HTTP_201_CREATED)

class AcceptReferralView(APIView):
    """
    Facility accepts a pending referral.
    """

    def patch(self, request, referral_id):
        try:
            referral = Referral.objects.get(id=referral_id)
        except Referral.DoesNotExist:
            return Response({"error": "Referral not found"}, status=status.HTTP_404_NOT_FOUND)

        if referral.status != "PENDING":
            return Response({"error": "Referral cannot be accepted"}, status=status.HTTP_400_BAD_REQUEST)

        referral.status = "ACCEPTED"
        referral.save()

        return Response(ReferralSerializer(referral).data)

class DispatchReferralView(APIView):
    """
    Assign transport and mark referral as IN_TRANSIT.
    """

    def patch(self, request, referral_id):
        transport_id = request.data.get("transport_id")

        try:
            referral = Referral.objects.get(id=referral_id)
            transport = Transport.objects.get(id=transport_id)
        except (Referral.DoesNotExist, Transport.DoesNotExist):
            return Response({"error": "Referral or transport not found"}, status=status.HTTP_404_NOT_FOUND)

        if referral.status != "ACCEPTED":
            return Response({"error": "Referral must be accepted first"}, status=status.HTTP_400_BAD_REQUEST)

        if transport.status != "available":
            return Response({"error": "Transport is not available"}, status=status.HTTP_400_BAD_REQUEST)

        # Assign transport
        referral.transport = transport
        referral.status = "IN_TRANSIT"
        referral.save()

        transport.status = "busy"
        transport.assigned_referral = referral
        transport.save()

        return Response({"message": "Referral dispatched successfully"})

class CompleteReferralView(APIView):
    """
    Mark referral as completed with outcome.
    """

    def patch(self, request, referral_id):
        outcome = request.data.get("outcome")  # maternal_alive, maternal_deceased, etc.

        try:
            referral = Referral.objects.get(id=referral_id)
        except Referral.DoesNotExist:
            return Response({"error": "Referral not found"}, status=status.HTTP_404_NOT_FOUND)

        if referral.status != "IN_TRANSIT":
            return Response({"error": "Referral is not in transit"}, status=status.HTTP_400_BAD_REQUEST)

        referral.status = "COMPLETED"
        referral.outcome = outcome
        referral.save()

        # Free up transport
        if referral.transport:
            referral.transport.status = "available"
            referral.transport.assigned_referral = None
            referral.transport.save()

        return Response(ReferralSerializer(referral).data)
