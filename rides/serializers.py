from rest_framework import serializers
from .models import Driver, Location, Block 

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['car_make', 'car_model', 'car_registration_number', 'driver_license_id', 'driver_license_img']

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('name', 'lat', 'lng')

class LocationSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True)

    class Meta:
        model = Location
        fields = ('name', 'polygon', 'lat', 'lng', 'blocks')