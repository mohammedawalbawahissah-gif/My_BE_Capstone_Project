from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from core.models import Referral, EmergencyCase, HealthFacility, Transport
from django.contrib.auth.models import User
from .models import Patient
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PatientForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.services.referral_engine import generate_referral
from .serializers import PatientSerializer
from core.serializers import (
    RegisterUserSerializer,
    HealthFacilitySerializer,
    TransportSerializer,
    ReferralSerializer
)


# HOME / DASHBOARD

from django.shortcuts import render

def api_root(request):
    # Render the home page template
    return render(request, "home.html")

# Basic page views

# ===================== WEB PAGES =====================

def home(request):
    return render(request, "home.html")

def patients(request):
    return render(request, "patients.html")

def referrals(request):
    return render(request, "referrals.html")

def emergency(request):
    return render(request, "emergency.html")

def facilities(request):
    return render(request, "facilities.html")

def transport(request):
    return render(request, "transport.html")

def login_view(request):
    return render(request, "login.html")

def logout_view(request):
    return render(request, "logout.html")

def register(request):
    return render(request, "register.html")

def profile(request):
    return render(request, "profile.html")


# ===================== API (JSON) =====================

def api_home(request):
    return JsonResponse({"message": "Welcome to Neomat Care API"})

def api_patients(request):
    return JsonResponse({"patients": []})

def api_referrals(request):
    return JsonResponse({"referrals": []})

# Authentication views
def login_view(request):
    return render(request, "login.html")

def logout_view(request):
    return render(request, "logout.html")

def register_user(request):
    return render(request, "register.html")

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

# Simple welcome API
class WelcomeAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Welcome to Neomat Care API"}, status=status.HTTP_200_OK)

class PatientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

# Register user API
class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        return Response({"message": f"User {user.username} created"}, status=status.HTTP_201_CREATED)


# Referral creation API
class ReferralCreateAPIView(APIView):
    def post(self, request):
        patient_name = request.data.get("patient_name")
        emergency_type = request.data.get("emergency_type")
        if not patient_name or not emergency_type:
            return Response({"error": "Patient name and emergency type required"}, status=status.HTTP_400_BAD_REQUEST)
        # Here you would normally save to the Referral model
        return Response({"message": f"Referral for {patient_name} ({emergency_type}) created"}, status=status.HTTP_201_CREATED)


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


# List all patients
def patients(request):
    patients = Patient.objects.all().order_by('-created_at')
    return render(request, 'patients.html', {'patients': patients})

# View a single patient's details
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patient_detail.html', {'patient': patient})

# Add a new patient
def patient_add(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patients')
    else:
        form = PatientForm()
    return render(request, 'patient_form.html', {'form': form, 'patient': None})

# Edit an existing patient
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patient_form.html', {'form': form, 'patient': patient})

# Optional: Delete a patient
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patients')
    return render(request, 'patient_confirm_delete.html', {'patient': patient})

# core/views.py

def patients(request):
    # Get query parameter from URL for filtering/sorting
    risk_filter = request.GET.get('risk', 'all')  # 'High', 'Medium', 'Low', or 'all'
    
    if risk_filter in ['High', 'Medium', 'Low']:
        patients = Patient.objects.filter(pregnancy_risk_level=risk_filter).order_by('-id')
    else:
        # Default: show all, sorted by risk priority: High > Medium > Low
        patients = Patient.objects.all()
        # Annotate sorting key: High=1, Medium=2, Low=3, Unknown=4
        patients = sorted(
            patients,
            key=lambda p: {'High':1, 'Medium':2, 'Low':3}.get(p.pregnancy_risk_level, 4)
        )
    
    context = {
        'patients': patients,
        'selected_risk': risk_filter,
    }
    return render(request, "patients.html", context)