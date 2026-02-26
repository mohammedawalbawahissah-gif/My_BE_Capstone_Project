from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
timezone.now()  

class User(AbstractUser):
    ROLE_CHOICES = (
        ('health_worker', 'Health Worker'),
        ('facility_admin', 'Facility Admin'),
        ('transport_officer', 'Transport_Officer'),
        ('system_admin', 'System Admin'),
        
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# core/models.py

class Patient(models.Model):
    first_name = models.CharField(max_length=100, default='Unknown')
    last_name = models.CharField(max_length=100, default='Unknown')
    date_of_birth = models.DateField(default=None, null=True)
    gender = models.CharField(max_length=10, default='Unknown')
    # Add other fields as needed

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class HealthFacility(models.Model):
    LEVEL_CHOICES = (
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('tertiary', 'Tertiary'),
    )

    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    available_services = models.JSONField()
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

class EmergencyCase(models.Model):
    patient_age = models.IntegerField()
    gestational_age = models.IntegerField()
    danger_signs = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Referral(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    emergency = models.BooleanField(default=False)
    referring_facility = models.ForeignKey(
        HealthFacility, related_name='referrals_out', on_delete=models.CASCADE
    )
    receiving_facility = models.ForeignKey(
        HealthFacility, related_name='referrals_in', on_delete=models.CASCADE
    )
    transport = models.ForeignKey(
        'Transport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    outcome = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class Transport(models.Model):
    TRANSPORT_TYPE_CHOICES = (
        ('ambulance', 'Ambulance'),
        ('motorbike', 'Motorbike'),
        ('car', 'Car'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance'),
    )

    facility = models.ForeignKey(
        HealthFacility,
        related_name='transports',
        on_delete=models.CASCADE
    )
    transport_type = models.CharField(
        max_length=20,
        choices=TRANSPORT_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    capacity = models.IntegerField(
        help_text="Number of patients that can be transported"
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transport_type} - {self.facility.name}"

from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Patient(models.Model):
    # Basic Identification
    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male','Male'), ('Female','Female')])
    marital_status = models.CharField(max_length=20, choices=[('Single','Single'), ('Married','Married'), ('Divorced','Divorced'), ('Widowed','Widowed')])
    
    # Contact Info
    contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Pregnancy Information
    gravida = models.IntegerField(blank=True, null=True)  # Number of pregnancies
    parity = models.IntegerField(blank=True, null=True)   # Number of births
    lmp = models.DateField(blank=True, null=True)         # Last Menstrual Period
    edd = models.DateField(blank=True, null=True)         # Expected Date of Delivery
    pregnancy_risk_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Medical Information
    diagnosis = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)  # e.g., diabetes, hypertension
    
    # Administrative
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"

class Patient(models.Model):
    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100, default='Unknown')
    last_name = models.CharField(max_length=50, default='Unknown')
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, default='Unknown')
    marital_status = models.CharField(max_length=20, default='Unknown')
    gravida = models.IntegerField(default=0)
    parity = models.IntegerField(default=0)
    lmp = models.DateField(default=None, null=True)  # Last Menstrual Period
    edd = models.DateField(default=None, null=True)  # Expected Date of Delivery
    diagnosis = models.TextField(default='')
    pregnancy_risk_level = models.CharField(max_length=20, default='Unknown')
    blood_group = models.CharField(max_length=5, default='Unknown')
    contact = models.CharField(max_length=15, default='Unknown')


    def __str__(self):
        return self.name


class HealthFacility(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Transport(models.Model):
    vehicle_number = models.CharField(max_length=50, default='N/A')
    driver_name = models.CharField(max_length=100, default='Unknown')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.vehicle_number


class Emergency(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Emergency - {self.patient.name}"


class Referral(models.Model):
    STATUS = (
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("In Transit", "In Transit"),
        ("Completed", "Completed"),
    )

    emergency = models.BooleanField(default=False)
    from_facility = models.ForeignKey(HealthFacility, on_delete=models.SET_NULL, null=True, related_name="from_facility")
    to_facility = models.ForeignKey(HealthFacility, on_delete=models.SET_NULL, null=True, related_name="to_facility")
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Referral for {self.emergency.patient.name}"