from django import forms
from .models import Patient, Emergency


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
            "email",
            "address",
            "gravida",
            "parity",
            "edd",
            "marital_status",
            "pregnancy_risk_level",
            "blood_type",
            "allergies",
            "diagnosis",
            "notes",
            "next_of_kin",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "allergies": forms.Textarea(attrs={"rows": 3}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "edd": forms.DateInput(attrs={"type": "date"}),
        }


class EmergencyForm(forms.ModelForm):
    class Meta:
        model = Emergency
        fields = [
            "patient",
            "description",
            "severity",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the emergency"}),
            "severity": forms.Select(),
        }