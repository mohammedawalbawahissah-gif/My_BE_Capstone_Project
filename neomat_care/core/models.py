from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


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


FACILITY_TYPE_CHOICES = [
    ('Hospital', 'Hospital'),
    ('Clinic', 'Clinic'),
    ('Health Center', 'Health Center'),
]

class HealthFacility(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    facility_type = models.CharField(
    max_length=50,
    choices=FACILITY_TYPE_CHOICES,
    default='Health Center'  # <- default set here
)

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=50, choices=FACILITY_TYPE_CHOICES)


class Transport(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance'),
    )
    vehicle_number = models.CharField(max_length=50)
    driver = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, related_name="transports")

    def __str__(self):
        return f"{self.vehicle_number} ({self.get_status_display()})"


    

class Patient(models.Model):

    RISK_LEVEL_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    pregnancy_risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default='Low'
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
    edd = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)

    blood_type = models.CharField(max_length=3, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    next_of_kin = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"

def calculate_risk_level(self):
    """
    Simple maternal risk assessment
    """

    # High risk conditions
    if self.age and self.age >= 35:
        return "High"

    if self.gravida and self.gravida >= 5:
        return "High"

    if self.parity and self.parity >= 4:
        return "High"

    if self.diagnosis:
        keywords = ["hypertension", "preeclampsia", "bleeding", "diabetes"]
        for word in keywords:
            if word in self.diagnosis.lower():
                return "High"

    # Medium risk
    if self.gravida and self.gravida >= 3:
        return "Medium"

    return "Low"

def save(self, *args, **kwargs):

    # Calculate risk level automatically
    self.pregnancy_risk_level = self.calculate_risk_level()

    super().save(*args, **kwargs)

    # Automatically create emergency alert for high-risk pregnancy
    if self.pregnancy_risk_level == "High":
        EmergencyAlert.objects.create(
            patient=self,
            alert_type="High Risk Pregnancy",
            description="Patient automatically flagged as high risk."
        )

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
    status = models.CharField(
    max_length=20,
    default="active"
)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emergency: {self.patient.first_name} ({self.severity})"


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

    @property
    def patient(self):
        # Allows templates to do referral.patient.name
        return self.emergency.patient

class EmergencyAlert(models.Model):
    patient = models.ForeignKey(
        'Patient', on_delete=models.CASCADE, related_name='emergency_alerts'
    )
    alert_type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.patient} at {self.created_at}"