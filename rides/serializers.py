from dataclasses import fields
from rest_framework import serializers, status
from django.core.files.base import ContentFile
from rest_framework.authentication import get_user_model
from .models import Driver, DriverLocation, Location, Block 
import base64
from user_account.models import User

User = get_user_model()

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
    

class UserDriverDetailsSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email',required=False)
    fullname = serializers.CharField(source='user.fullname',required=False)
    phone_no = serializers.CharField(source='user.phone_no',required=False)
    birthdate = serializers.DateTimeField(source='user.birthdate', required=False)
    profile_img = serializers.CharField(source='user.profile_img', required=False)
    profile_img_url = serializers.SerializerMethodField()
    gender = serializers.CharField(source='user.gender',required=False)
    nationality = serializers.CharField(source='user.nationality',required=False)

    def get_profile_img_url(self,instance):
        return instance.user.get_profile_img_url()


    class Meta:
        model = Driver
        fields = ('user_id','email', 'fullname', 'phone_no', 'birthdate','gender','nationality','profile_img','profile_img_url')
        read_only_fields = ['user_id', 'profile_img_url']

    def update(self, instance, validated_data):
        try:
            # Extract user-related fields from validated_data
            user_data = validated_data.pop('user', {})

            # Update the associated User object's fields
            user = instance.user
            if 'email' in user_data:
                email = user_data['email']
                if email != user.email:
                    if User.objects.filter(email=email).exclude(id=user.id).exists():
                        error_msg = {
                            "success": False,
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "error": "Bad Request",
                            "message": "Email already exists",
                        }
                        raise serializers.ValidationError(error_msg)
                    user.email = email
                    user.username = email.split('@')[0]

            user.fullname = user_data.get('fullname', user.fullname)
            user.phone_no = user_data.get('phone_no', user.phone_no)
            user.birthdate = user_data.get('birthdate', user.birthdate)
            user.gender = user_data.get('gender', user.gender)
            user.nationality = user_data.get('nationality', user.nationality)
            
            if user_data.get('profile_img'):
                profile_img = user_data.get('profile_img')
                format, imgstr = profile_img.split(';base64,') 
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'{user.username}_profile.{ext}')
                user.profile_img = data
            
            user.save()

            # Update the Driver object's fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            return instance
        except serializers.ValidationError as e:
            error_msg = {
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": e.detail,
            }
            raise serializers.ValidationError(error_msg)

        except Exception as e:
            print(e)
            error_msg = {
                "success": False,
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal Server Error",
                "message": "Failed to update driver",
            }
            raise serializers.ValidationError(error_msg)

class DriverVehicleInfo(serializers.ModelSerializer):

    vehicle_manufacturer = serializers.CharField(required=False)
    vehicle_model = serializers.CharField(required=False)
    vehicle_color = serializers.CharField(required=False)
    vehicle_ownership = serializers.CharField(required=False)
    vehicle_registration_number = serializers.CharField(required=False)

    class Meta:
        model = Driver
        fields = ('vehicle_manufacturer', 'vehicle_model', 'vehicle_color', 'vehicle_ownership', 'vehicle_registration_number')

class DriverLocationSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)

    class Meta:
        model = DriverLocation
        fields = ['user_id','latitude', 'longitude']


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
