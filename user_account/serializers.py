from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, StudentID
from django.shortcuts import get_list_or_404, get_object_or_404



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'native_name','phone_no','role','isVerified']

    # def create(self, validated_data):
    #     role = validated_data.pop('role')
    #     user = User.objects.create(**validated_data)
    #     if role == 'student':
    #         student_data = validated_data.pop('student')
    #         Student.objects.create(user=user, **student_data)
    #     else:
    #         staff_data = validated_data.pop('staff')
    #         Staff.objects.create(user=user, **staff_data)
    #     return user

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
