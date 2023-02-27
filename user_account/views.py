from django.shortcuts import render
from rest_framework import generics, permissions, status, serializers
from .serializers import UserSerializer, AuthTokenSerializer, RegisterSerializer, StudentIDVerificationSerializer,PasswordResetConfirmSerializer, PasswordResetSerializer, ProfilePictureSerializer
from django.shortcuts import render
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import login, get_user_model, update_session_auth_hash
from rest_framework.views import APIView
from .models import StudentID
from django.contrib.auth.tokens import default_token_generator as auth_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from mytaxi import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .models import User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import sys
from django.core.mail import EmailMessage
from .models import StudentID
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import default_storage



User = get_user_model()

# Create your views here.
class UserRetrieveAPIView(generics.RetrieveAPIView):
    User =get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except serializers.ValidationError as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": "Email already exists",
                "line": sys.exc_info()[-1].tb_lineno
            }, status=status.HTTP_400_BAD_REQUEST)

        current_site = get_current_site(request)
        subject = 'Verify your email address'
        message = render_to_string('verification_email.html', {
            'user': user,
            'native_name': user.native_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': auth_token_generator.make_token(user),
        })

        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email], html_message=message)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
            return super(LoginAPI, self).post(request, format=None)
        except serializers.ValidationError as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "error": "Bad Request",
                "message": str(e),
                "line": sys.exc_info()[-1].tb_lineno
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "error": "Unauthorized",
                "message": "Unable to authenticate with provided credentials",
                "line": sys.exc_info()[-1].tb_lineno
            }, status=status.HTTP_401_UNAUTHORIZED)

class StudentIDVerificationView(APIView):
    # serializer_class = StudentIDVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = StudentIDVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_number = serializer.validated_data['id_number']
        try:
            if StudentID.objects.get(user=request.user).DoesNotExist or StudentID.objects.get(id_number=id_number).DoesNotExist:
                return  Response({
                            "success": False,
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "error": "Bad Request",
                            "message": "User already has a Student ID",
                        }, status=status.HTTP_400_BAD_REQUEST)

        except StudentID.DoesNotExist:
            student = StudentID.objects.create(user= request.user, id_number=id_number, verification_status=True)
            student.save()
            request.user.isVerified = True
            request.user.save()
            return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "message": "ID Verified",
                }, status=status.HTTP_200_OK)


@api_view(['GET'])
def verify_email(request, uidb64, token):

    User =get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and auth_token_generator.check_token(user, token):
        user.isVerified = True
        user.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Your email address has been verified.",
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "success": False,
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "error": "Bad Request",
            "message": "Verification link is invalid!",
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(generics.GenericAPIView):
    
    serializer_class = PasswordResetSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = User.objects.get(email=serializer.data['email'])
                    if user.isVerified:
                        send_password_reset_email(request, user)
                        return Response({
                                    "success": True,
                                    "statusCode": status.HTTP_200_OK,
                                    "message": "Password reset email sent",
                                })
                    else:
                        return Response({
                            "success": False,
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "error": "Bad Request",
                            "message": "User not verified",
                        }, status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return Response({
                        "success": False,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "error": "Bad Request",
                        "message": "User not found",
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "error": "Bad Request",
                    "message": "Invalid request data",
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
            "success": False,
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Internal Server Error",
            "message": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    
def send_password_reset_email(request, user):

    current_site = get_current_site(request)
    subject = 'Do Not Reply: Password reset request'
    message = render_to_string('password_reset_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': auth_token_generator.make_token(user),
    })
    to_email = user.email
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email], html_message=message)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            if 'new_password1' not in request.data:
                return  Response({
                            "success": False,
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "error": "Bad Request",
                            "message": "new_password1 field is missing from the request payload",
                        }, status=status.HTTP_400_BAD_REQUEST)
            try:
                 
                uid = force_str(urlsafe_base64_decode(serializer.data['uid']))
                user = User.objects.get(pk=uid)
                user.set_password(serializer.data['new_password1'])
                user.full_clean()
                user.save()
                update_session_auth_hash(request, user)
                token = AuthToken.objects.create(user)[1]
                return Response({'token': token})
            except ValidationError as e:
                return Response({'error': e})
        else:
            print(serializer.errors) # add this line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateAPI(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        return Response(data)

        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        # if user.role == 'student':
        #     student_id = StudentID.objects.get(user=user)
        #     student_id_serializer = StudentIDVerificationSerializer(student_id, data=request.data)
        #     if student_id_serializer.is_valid():
        #         student_id_serializer.save()
        user_serializer = UserSerializer(user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "message": "User details updated",
                "data": UserSerializer(user).data
            })
        return Response({
            "success": False,
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "error": "Bad Request",
            "message": user_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            users = self.get_queryset()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                "detail": str(e)
            }, status=status.HTTP_404_NOT_FOUND)


class ProfilePictureView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilePictureSerializer
    
    def get_object(self):
        return self.request.user