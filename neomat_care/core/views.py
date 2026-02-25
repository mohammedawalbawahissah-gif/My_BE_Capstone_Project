from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from core.models import Referral, EmergencyCase, HealthFacility, Transport
from core.serializers import (
    RegisterUserSerializer,
    HealthFacilitySerializer,
    TransportSerializer,
    ReferralSerializer
)
from core.services.referral_engine import generate_referral

# HOME / DASHBOARD
def home(request):
    return render(request, "home.html")


@login_required
def home_view(request):
    return render(request, "home.html")


@login_required
def dashboard_view(request):
    return render(request, "home.html")


@login_required
def patients_view(request):
    return render(request, "patients.html")


@login_required
def referrals_view(request):
    return render(request, "referrals.html")


@login_required
def emergency_view(request):
    return render(request, "emergency.html")


@login_required
def facilities_view(request):
    return render(request, "facilities.html")


@login_required
def transport_view(request):
    return render(request, "transport.html")


@login_required
def profile_view(request):
    return render(request, "profile.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("login")

    return render(request, "register.html")

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "logout.html")

User = get_user_model()

# -------------------- API Views --------------------
class RegisterUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny] 

class SuggestReferralView(APIView):
    def post(self, request):
        case_id = request.data.get("emergency_case_id")
        latitude = request.data.get("current_latitude")
        longitude = request.data.get("current_longitude")

        if not all([case_id, latitude, longitude]):
            return Response({"error": "emergency_case_id, current_latitude, current_longitude are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            case = EmergencyCase.objects.get(id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Emergency case not found"}, status=status.HTTP_404_NOT_FOUND)

        result = generate_referral(case, latitude, longitude)

        if not result["facility"]:
            return Response({"error": "No suitable facility found"}, status=status.HTTP_404_NOT_FOUND)

        facility_data = HealthFacilitySerializer(result["facility"]).data
        transport_data = TransportSerializer(result["transport"][0]).data if result["transport"] else None

        return Response({
            "priority": result["priority"],
            "recommended_facility": facility_data,
            "transport": transport_data
        }, status=status.HTTP_200_OK)

class CreateReferralView(APIView):
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

        referral.transport = transport
        referral.status = "IN_TRANSIT"
        referral.save()

        transport.status = "busy"
        transport.assigned_referral = referral
        transport.save()

        return Response({"message": "Referral dispatched successfully"})

class CompleteReferralView(APIView):
    def patch(self, request, referral_id):
        outcome = request.data.get("outcome")

        try:
            referral = Referral.objects.get(id=referral_id)
        except Referral.DoesNotExist:
            return Response({"error": "Referral not found"}, status=status.HTTP_404_NOT_FOUND)

        if referral.status != "IN_TRANSIT":
            return Response({"error": "Referral is not in transit"}, status=status.HTTP_400_BAD_REQUEST)

        referral.status = "COMPLETED"
        referral.outcome = outcome
        referral.save()

        if referral.transport:
            referral.transport.status = "available"
            referral.transport.assigned_referral = None
            referral.transport.save()

        return Response(ReferralSerializer(referral).data)

# -------------------- API Root --------------------
@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Neomat Care API",
        "endpoints": {
            "register": "/api/register/",
            "login": "/api/login/",
            "create_referral": "/api/referrals/create/",
            "suggest_referral": "/api/referrals/suggest/"
        }
    })

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "User already exists"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return JsonResponse({"message": "User registered successfully"})

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

from .models import EmergencyCase  # make sure this model exists

@csrf_exempt
def create_emergency(request):
    if request.method == "POST":
        data = json.loads(request.body)
        case = EmergencyCase.objects.create(
            patient_name=data.get("patient_name"),
            condition=data.get("condition"),
            severity=data.get("severity"),
            created_by=request.user
        )
        return JsonResponse({"message": "Emergency recorded", "case_id": case.id})

from .models import Referral

@csrf_exempt
def create_referral(request):
    if request.method == "POST":
        data = json.loads(request.body)
        case_id = data.get("case_id")
        case = EmergencyCase.objects.get(id=case_id)

        referral = Referral.objects.create(
            emergency_case=case,
            referred_to=data.get("facility"),
            reason=data.get("reason"),
            status="Pending"
        )
        return JsonResponse({"message": "Referral created", "referral_id": referral.id})

from .models import Transport

@csrf_exempt
def dispatch_transport(request):
    if request.method == "POST":
        data = json.loads(request.body)
        referral_id = data.get("referral_id")
        referral = Referral.objects.get(id=referral_id)

        transport = Transport.objects.create(
            referral=referral,
            driver_name=data.get("driver"),
            vehicle_number=data.get("vehicle"),
            status="En Route"
        )

        referral.status = "Transport Dispatched"
        referral.save()

        return JsonResponse({"message": "Ambulance dispatched successfully"})