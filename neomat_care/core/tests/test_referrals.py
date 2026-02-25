from django.test import TestCase
from rest_framework.test import APIClient
from core.models import User, EmergencyCase
from rest_framework import status

class EmergencyCaseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="nurse@clinic.com", password="test123", role="health_worker")
        response = self.client.post('/api/auth/login/', {'email': 'nurse@clinic.com', 'password': 'test123'}, format='json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_emergency_case(self):
        data = {
            "patient_age": 28,
            "gestational_age": 38,
            "danger_signs": {"bleeding": True, "high_bp": False}
        }
        response = self.client.post('/api/emergency-cases/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EmergencyCase.objects.count(), 1)

from core.models import Referral, EmergencyCase, AuditLog, HealthFacility

class ReferralWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="doctor@hospital.com", password="test123", role="health_worker")
        self.facility = HealthFacility.objects.create(name="City Hospital", latitude=0, longitude=0, capacity=5)
        self.case = EmergencyCase.objects.create(patient_age=25, gestational_age=37, danger_signs={"bleeding": True}, created_by=self.user)
        response = self.client.post('/api/auth/login/', {'email': 'doctor@hospital.com', 'password': 'test123'}, format='json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_referral_and_audit_log(self):
        data = {
            "case_id": self.case.id
        }
        response = self.client.post('/api/referrals/create/', data, format='json')
        self.assertEqual(response.status_code, 201)
        referral = Referral.objects.first()
        self.assertIsNotNone(referral)
        # Audit log check
        audit = AuditLog.objects.filter(referral=referral, action="CREATE_REFERRAL").first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.user, self.user)