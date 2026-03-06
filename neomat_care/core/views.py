from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import (
    Patient,
    Emergency,
    EmergencyAlert,
    Referral,
    Transport,
    HealthFacility
)
from .forms import PatientForm, EmergencyForm
from .serializers import PatientSerializer, ReferralSerializer, RegisterUserSerializer
from core.services.referral_engine import generate_referral

User = get_user_model()

# ================================
# API Views
# ================================

def api_home(request):
    return JsonResponse({"status": "ok", "message": "Neomat Care API"})

class APIHomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Welcome to Neomat Care API"})

class PatientListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReferralCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        emergency_id = request.data.get("emergency_id")
        receiving_facility_id = request.data.get("receiving_facility_id")

        try:
            emergency = Emergency.objects.get(id=emergency_id)
            receiving_facility = HealthFacility.objects.get(id=receiving_facility_id)
        except (Emergency.DoesNotExist, HealthFacility.DoesNotExist):
            return Response({"error": "Invalid emergency or facility"}, status=status.HTTP_404_NOT_FOUND)

        referral = Referral.objects.create(
            emergency=emergency,
            referring_facility=emergency.created_by.healthfacility_set.first() if emergency.created_by else None,
            receiving_facility=receiving_facility,
            status="pending",
        )
        serializer = ReferralSerializer(referral)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ================================
# Authentication Views
# ================================

def login_logout_view(request):
    if request.method == "POST":
        if "logout" in request.POST:
            logout(request)
            return redirect("login_logout")

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "auth/login_logout.html", {"error": "Invalid credentials"})
    return render(request, "auth/login_logout.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})
        User.objects.create_user(username=username, password=password, email=email)
        return redirect("login_logout")
    return render(request, "register.html")

# ================================
# Template Views (Protected)
# ================================

@login_required
def home(request):
    # Summary stats
    total_patients = Patient.objects.count()
    active_referrals = Referral.objects.filter(status__in=["pending","accepted","in_transit"]).count()
    emergencies_count = Emergency.objects.exclude(status="resolved").count()

    # Transport & health facilities
    transports = Transport.objects.all()
    referring_facilities = HealthFacility.objects.filter(facility_type='Referring')
    receiving_facilities = HealthFacility.objects.filter(facility_type='Receiving')

    context = {
        "total_patients": total_patients,
        "active_referrals": active_referrals,
        "emergencies": emergencies_count,
        "transports": transports,
        "referring_facilities": referring_facilities,
        "receiving_facilities": receiving_facilities,
    }

    return render(request, "dashboard/home.html", context)

@login_required
def dashboard(request):
    # High-risk patients
    high_risk_patients = Patient.objects.filter(pregnancy_risk_level='High')

    # Emergency alerts (latest 5, unresolved)
    emergency_alerts = EmergencyAlert.objects.filter(resolved=False).order_by("-created_at")[:5]
    emergency_alerts_list = [
        {"patient_name": alert.patient.first_name + " " + alert.patient.last_name, "timestamp": alert.created_at}
        for alert in emergency_alerts
    ]

    # Transport & health facilities
    transports = Transport.objects.all()
    referring_facilities = HealthFacility.objects.filter(facility_type='Referring')
    receiving_facilities = HealthFacility.objects.filter(facility_type='Receiving')

    context = {
        "high_risk_patients": high_risk_patients,
        "emergency_alerts": emergency_alerts_list,
        "transports": transports,
        "referring_facilities": referring_facilities,
        "receiving_facilities": receiving_facilities,
    }

    return render(request, "core/dashboard.html", context)

# ================================
# Patient CRUD Views
# ================================

@login_required
def patients(request):
    paginator = Paginator(Patient.objects.all(), 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "patients.html", {"patients": page_obj})

@login_required
def patient_add(request):
    form = PatientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("patients")
    return render(request, "patient_form.html", {"form": form})

@login_required
def patient_edit(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        return redirect("patients")
    return render(request, "patient_form.html", {"form": form})

@login_required
def patient_delete(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.delete()
        return redirect("patients")
    return render(request, "patient_confirm_delete.html", {"patient": patient})

# ================================
# Emergency Views
# ================================

@login_required
def create_emergency(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        description = request.POST.get("description")
        emergency = Emergency.objects.create(
            patient=patient,
            description=description,
            created_by=request.user,
            active=True,
        )
        referral_data = generate_referral(emergency)
        if referral_data.get("facility"):
            Referral.objects.create(
                emergency=emergency,
                referring_facility=request.user.healthfacility_set.first(),
                receiving_facility=referral_data["facility"],
                transport=referral_data.get("transport"),
                status="pending",
            )
        return redirect("referrals")
    return render(request, "emergency.html", {"patient": patient})

@login_required
def emergency_view(request):
    return render(request, "emergency.html")

@login_required
def emergency_create(request):
    form = EmergencyForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("emergency_status")
    return render(request, "core/emergency_create.html", {"form": form})

# ================================
# Referrals, Facilities, Transport Views
# ================================

@login_required
def referrals(request):
    referrals_qs = Referral.objects.select_related(
        "emergency",
        "referring_facility",
        "receiving_facility",
        "transport",
    )
    return render(request, "referrals.html", {"referrals": referrals_qs})

@login_required
def facilities(request):
    return render(request, "facilities.html", {"facilities": HealthFacility.objects.all()})

@login_required
def transport(request):
    return render(request, "transport.html", {"transports": Transport.objects.select_related("facility")})

# ================================
# API Views for Patients and Referrals
# ================================

@api_view(["GET"])
def api_patients(request):
    serializer = PatientSerializer(Patient.objects.all(), many=True)
    return Response(serializer.data)

@api_view(["GET"])
def api_referrals(request):
    referrals = Referral.objects.select_related(
        "emergency",
        "referring_facility",
        "receiving_facility",
        "transport",
    )
    serializer = ReferralSerializer(referrals, many=True)
    return Response(serializer.data)