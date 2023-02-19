from rest_framework import serializers
from .models import Driver

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['car_make', 'car_model', 'car_registration_number', 'driver_license_id', 'driver_license_img']