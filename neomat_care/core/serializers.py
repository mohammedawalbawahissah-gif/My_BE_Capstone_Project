from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Patient, HealthFacility, Transport, Referral, Emergency

User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'health_worker')
        )
        return user


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class EmergencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Emergency
        fields = "__all__"


class ReferralSerializer(serializers.ModelSerializer):
    emergency = EmergencySerializer(read_only=True)
    referring_facility = serializers.StringRelatedField()
    receiving_facility = serializers.StringRelatedField()
    transport = serializers.StringRelatedField()

    class Meta:
        model = Referral
        fields = "__all__"


class HealthFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthFacility
        fields = "__all__"

class TransportSerializer(serializers.ModelSerializer):
    facility = HealthFacilitySerializer(read_only=True)

    class Meta:
        model = Transport
        fields = "__all__"