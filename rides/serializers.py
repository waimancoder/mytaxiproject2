from rest_framework import serializers
from django.core.files.base import ContentFile
from .models import Driver, Location, Block 
import base64

class DriverLicenseSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    driver_license_img_front = serializers.CharField()
    driver_license_img_back = serializers.CharField()

    class Meta:
        model = Driver
        fields = ['user_id','driver_license_img_front', 'driver_license_img_back']
        read_only_fields = ['user_id']

    def update(self, instance, validated_data):
        print("Update method called")
        driver_license_img_front = validated_data.get('driver_license_img_front', None)
        driver_license_img_back = validated_data.get('driver_license_img_back', None)
        
        if driver_license_img_front:
            # Decode the base64-encoded image data
            format, imgstr = driver_license_img_front.split(';base64,') 
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{instance.user_id}_driver_license_img_front.{ext}')

            instance.driver_license_img_front = data
            instance.save()
        
        if driver_license_img_back:
            # Decode the base64-encoded image data
            format, imgstr = driver_license_img_back.split(';base64,') 
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{instance.user_id}_driver_license_img_back.{ext}')

            instance.driver_license_img_back = data
            instance.save()
        return instance
    

class DriverIdConfirmationSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    idConfirmation = serializers.CharField()

    class Meta:
        model = Driver
        fields = ['user_id','idConfirmation']
        read_only_fields = ['user_id']
    
    def update(self, instance, validated_data):
        print("Update method called")
        idConfirmation = validated_data.get('idConfirmation', None)
        
        if idConfirmation:
            # Decode the base64-encoded image data
            format, imgstr = idConfirmation.split(';base64,') 
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{instance.user_id}_idConfirmation.{ext}')

            instance.idConfirmation = data
            instance.save()

        return instance
    

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('name', 'lat', 'lng')

class LocationSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True)

    class Meta:
        model = Location
        fields = ('name', 'polygon', 'lat', 'lng', 'blocks')

    def create(self, validated_data):
        blocks_data = validated_data.pop('blocks')
        location = Location.objects.create(**validated_data)
        for block_data in blocks_data:
            Block.objects.create(location=location, **block_data)
        return location
    
    def update(self, instance, validated_data):
        blocks_data = validated_data.pop('blocks')
        blocks = list(instance.blocks.all())

        instance.name = validated_data.get('name', instance.name)
        instance.polygon = validated_data.get('polygon', instance.polygon)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.lng = validated_data.get('lng', instance.lng)
        instance.save()

        for block_data in blocks_data:
            if blocks:
                block = blocks.pop(0)
                block.name = block_data.get('name', block.name)
                block.lat = block_data.get('lat', block.lat)
                block.lng = block_data.get('lng', block.lng)
                block.save()
            else:
                Block.objects.create(location=instance, **block_data)

        for block in blocks:
            block.delete()

        return instance
