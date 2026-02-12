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

