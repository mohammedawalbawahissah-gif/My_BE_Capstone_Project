# core/views.py
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Patient, Emergency, Referral, Transport, HealthFacility
from .forms import PatientForm, EmergencyForm
from .serializers import PatientSerializer, RegisterUserSerializer, HealthFacilitySerializer, TransportSerializer, ReferralSerializer
from core.services.referral_engine import generate_referral


User = get_user_model()


# =========================
# API VIEWS
# =========================
@api_view(['GET'])
def api_home(request):
    return Response({"message": "Welcome to Neomat Care API"})

@api_view(['GET'])
def api_patients(request):
    patients = Patient.objects.all()
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_referrals(request):
    referrals = Referral.objects.all()
    serializer = ReferralSerializer(referrals, many=True)
    return Response(serializer.data)

# =========================
# AUTHENTICATION
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username exists"})
        User.objects.create_user(username=username, password=password, email=email)
        return redirect("login")
    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("login")

# =========================
# DASHBOARD
# =========================
@login_required
def home(request):
    total_patients = Patient.objects.count()
    high_risk = Patient.objects.filter(pregnancy_risk_level="High").count()
    active_referrals = Referral.objects.filter(status__in=["pending", "accepted", "in_transit"]).count()
    emergencies = Emergency.objects.filter(active=True).count()

    context = {
        "total_patients": total_patients,
        "high_risk": high_risk,
        "active_referrals": active_referrals,
        "emergencies": emergencies,
    }
    return render(request, "dashboard.html", context)


# =========================
# PATIENT MANAGEMENT
# =========================
@login_required
def patients(request):
    # Filters
    risk_filter = request.GET.get("risk", "all")
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort", "id")
    order = request.GET.get("order", "asc")

    patients_qs = Patient.objects.all()

    if risk_filter in ["High", "Medium", "Low"]:
        patients_qs = patients_qs.filter(pregnancy_risk_level=risk_filter)

    if search_query:
        patients_qs = patients_qs.filter(
            Q(patient_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(diagnosis__icontains=search_query)
        )

    sortable_fields = ["age", "gravida", "parity", "edd", "last_name", "first_name"]
    if sort_by in sortable_fields:
        patients_qs = patients_qs.order_by(f"-{sort_by}" if order == "desc" else sort_by)
    else:
        patients_qs = patients_qs.order_by("id")

    paginator = Paginator(patients_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    context = {
        "patients": page_obj,
        "selected_risk": risk_filter,
        "sort_by": sort_by,
        "order": order,
        "search_query": search_query,
    }
    return render(request, "patients.html", context)


@login_required
def patient_add(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("patients")
    else:
        form = PatientForm()
    return render(request, "patient_form.html", {"form": form})


@login_required
def patient_edit(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect("patients")
    else:
        form = PatientForm(instance=patient)
    return render(request, "patient_form.html", {"form": form, "patient": patient})


@login_required
def patient_delete(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.delete()
        return redirect("patients")
    return render(request, "patient_confirm_delete.html", {"patient": patient})


# =========================
# EMERGENCIES & REFERRALS
# =========================
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

        # Suggest referral automatically
        referral_result = generate_referral(emergency)
        if referral_result.get("facility"):
            receiving_facility = referral_result["facility"]
            transport = referral_result.get("transport")
            referral = Referral.objects.create(
                emergency=emergency,
                referring_facility=patient.created_by.healthfacility_set.first(),
                receiving_facility=receiving_facility,
                status="pending",
                transport=transport
            )

        return redirect("referrals")

    return render(request, "emergency.html", {"patient": patient})


@login_required
def referrals(request):
    referrals_qs = Referral.objects.select_related("emergency", "referring_facility", "receiving_facility", "transport")
    context = {"referrals": referrals_qs}
    return render(request, "referrals.html", context)


# =========================
# FACILITIES & TRANSPORT
# =========================
@login_required
def facilities(request):
    facilities_qs = HealthFacility.objects.all()
    return render(request, "facilities.html", {"facilities": facilities_qs})


@login_required
def transport(request):
    transport_qs = Transport.objects.select_related("facility")
    return render(request, "transport.html", {"transports": transport_qs})


# =========================
# API VIEWS
# =========================
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
            referring_facility=emergency.created_by.healthfacility_set.first(),
            receiving_facility=receiving_facility,
            status="pending"
        )
        serializer = ReferralSerializer(referral)
        return Response(serializer.data, status=status.HTTP_201_CREATED)