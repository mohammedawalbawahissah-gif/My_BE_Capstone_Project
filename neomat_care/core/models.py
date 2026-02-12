from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('health_worker', 'Health Worker'),
        ('facility_admin', 'Facility Admin'),
        ('transport_officer', 'Transport_Officer'),
        ('system_admin', 'System Admin'),
        
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

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

    emergency_case = models.ForeignKey(EmergencyCase, on_delete=models.CASCADE)
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
    created_at = models.DateTimeField(auto_now_add=True)
