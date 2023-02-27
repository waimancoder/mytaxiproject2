from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model, authenticate, update_session_auth_hash
from django.utils.translation import gettext_lazy as _
from .models import User, StudentID
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as auth_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
import os
import uuid
from django.conf import settings
from django.core.files.storage import get_storage_class


User = get_user_model()

class StudentIDNumberField(serializers.Field):

    def to_representation(self, obj):
        try:
            student_id = obj.studentid
            return student_id.id_number
        except StudentID.DoesNotExist:
            return None

class UserSerializer(serializers.ModelSerializer):
    id_number = StudentIDNumberField(source='*', read_only=True)


    class Meta:
        model = User
        fields = ['id', 'email', 'native_name', 'phone_no', 'role', 'isVerified','id_number']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['role'] != 'student':
            data.pop('id_number')
        return data

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=get_user_model().objects.all())
        ]
    )
    native_name = serializers.CharField(max_length=100)
    phone_no = serializers.CharField(max_length=12)


    class Meta:
        model = User
        fields = ('id', 'email','native_name','password','phone_no','role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
    
        username = validated_data['email'].split('@')[0]
        user = User.objects.create_user(username, validated_data['email'],validated_data['password'])
        user.native_name = validated_data['native_name']
        user.phone_no = validated_data['phone_no']
        user.role = validated_data['role']

        user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user_request = get_object_or_404(
                    User,
                    email=email,
                )
        username = user_request.username

        user = authenticate(
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class StudentIDVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentID
        fields = ['id_number']

class VerifyEmailSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'error': 'User not found'})

        if not auth_token_generator.check_token(user, data['token']):
            raise ValidationError({'error': 'Invalid token'})

        password_reset_form = SetPasswordForm(user, data)
        if not password_reset_form.is_valid():
            raise ValidationError(password_reset_form.errors)

        return data


class ProfilePictureSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('profile_img',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'profile_img' in ret and ret['profile_img']:
            # Get the profile image file from the storage backend
            image_file = instance.profile_img
            # Generate a URL for the image file
            url = image_file.url if image_file else None
            ret['profile_img'] = url
        return ret

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if 'profile_img' in data:
            profile_img = data['profile_img']
            if profile_img:
                # Generate a filename for the uploaded image
                storage = get_storage_class(settings.DEFAULT_FILE_STORAGE)()
                filename = storage.generate_filename(profile_img.name)
                # Save the image to the storage backend with the generated filename
                storage.save(filename, profile_img)
                # Set the profile_img field to the generated filename
                ret['profile_img'] = filename
            else:
                ret['profile_img'] = None
        return ret