# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# =========================
# CUSTOM USER
# =========================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('health_worker', 'Health Worker'),
        ('facility_admin', 'Facility Admin'),
        ('transport_officer', 'Transport Officer'),
        ('system_admin', 'System Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# =========================
# HEALTH FACILITY
# =========================
class HealthFacility(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    capacity = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name


# =========================
# TRANSPORT
# =========================
class Transport(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance'),
    )
    vehicle_number = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, related_name="transports")

    def __str__(self):
        return f"{self.vehicle_number} ({self.get_status_display()})"


# =========================
# PATIENT
# =========================
class Patient(models.Model):
    RISK_LEVEL_CHOICES = (
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    )
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    gravida = models.PositiveIntegerField(blank=True, null=True)
    parity = models.PositiveIntegerField(blank=True, null=True)
    edd = models.DateField(blank=True, null=True)  # Estimated delivery date
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    pregnancy_risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, blank=True, null=True)

    blood_type = models.CharField(max_length=3, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    pregnancy_risk_level = models.CharField(
        max_length=20,
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        default="Low",
        null=True,
        blank=True
    )    

    next_of_kin = models.CharField(max_length=100, blank=True, null=True)
    pregnancy_risk = models.CharField(
        max_length=10,
        choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
        blank=True,
        null=Trueco
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"


# =========================
# EMERGENCY
# =========================
class Emergency(models.Model):
    SEVERITY_CHOICES = (
        ('Critical', 'Critical'),
        ('Moderate', 'Moderate'),
        ('Mild', 'Mild'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="emergencies")
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Moderate')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emergency: {self.patient.first_name} ({self.severity})"


# =========================
# REFERRAL
# =========================
class Referral(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    emergency = models.OneToOneField(Emergency, on_delete=models.CASCADE, related_name="referral")
    referring_facility = models.ForeignKey(HealthFacility, related_name="referrals_out", on_delete=models.CASCADE)
    receiving_facility = models.ForeignKey(HealthFacility, related_name="referrals_in", on_delete=models.CASCADE)
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    outcome = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Referral for {self.emergency.patient.first_name} ({self.status})"