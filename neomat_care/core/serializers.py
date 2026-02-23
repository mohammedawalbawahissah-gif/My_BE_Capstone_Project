from rest_framework import serializers
from .models import User, HealthFacility, EmergencyCase, Referral, Transport

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class HealthFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthFacility
        fields = '__all__'


class EmergencyCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyCase
        fields = '__all__'

class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = '__all__'

class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'
