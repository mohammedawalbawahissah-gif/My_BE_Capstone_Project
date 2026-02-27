# core/forms.py
from django import forms
from .models import Patient, Emergency

# =========================
# PATIENT FORM
# =========================
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "patient_id",
            "first_name",
            "last_name",
            "age",
            "gender",
            "phone_number",
            "address",
            "diagnosis",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
        }

# =========================
# EMERGENCY FORM
# =========================
class EmergencyForm(forms.ModelForm):
    class Meta:
        model = Emergency
        fields = [
            "patient",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the emergency"}),
        }