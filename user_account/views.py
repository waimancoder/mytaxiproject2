import traceback
from django.http import Http404, JsonResponse
from rest_framework import generics, permissions, status, serializers, mixins, viewsets
from .serializers import UserSerializer, AuthTokenSerializer, RegisterSerializer, StudentIDVerificationSerializer,PasswordResetConfirmSerializer, PasswordResetSerializer, ProfilePictureSerializer
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator as auth_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from mytaxi import settings
from rest_framework.decorators import api_view
from .models import User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import sys
from django.core.mail import EmailMessage
from .models import StudentID
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.signals import user_logged_in



User = get_user_model()


def custom_500_page_not_found(request):
    tb = traceback.format_exc().splitlines()[-5:]
    error_msg = f"Internal Server Error: {tb}"
    return JsonResponse ({
                "success": False,
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal Server Error, Please Contact Server Admin",
                "exception": str(sys.exc_info()[1]),
                "traceback": error_msg
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def custom_404_page_not_found(request, exception):
    return JsonResponse ({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "error": "Page Not Found or Invalid API Endpoint",
            }, status=status.HTTP_404_NOT_FOUND)


# Create your views here. 
class UserRetrieveAPIView(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'options']
    lookup_field = 'id'



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
            'fullname': user.fullname,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': auth_token_generator.make_token(user),
        })
        
        # send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email], html_message=message)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })
    
    def options(self, request, *args, **kwargs):
        methods = ['POST', 'OPTIONS']
        content_types = ['application/json']
        headers = {
            'Allow': ', '.join(methods),
            'Content-Type': ', '.join(content_types),
        }
        return Response({"methods": methods, "content_types":content_types, "headers": headers
            },status=status.HTTP_200_OK, headers=headers)


class LoginAPI(KnoxLoginView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AuthTokenSerializer
    
    def post(self, request, format=None):
        
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)  # get User instance
            token_ttl = self.get_token_ttl()
            instance, token = AuthToken.objects.create(user, token_ttl)  # pass User instance to create()
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            data = self.get_post_response_data(request, token, instance)
            
            basicinfo = {
                "id" : user.id,
                "email" : user.email,
                "fullname" :user.fullname,
                "phone_no" : user.phone_no,
                "role" : user.role,
                "birthdate" : user.birthdate if user.birthdate else "",
                "gender": user.gender,
                "nationality" : user.nationality if user.nationality else "",
                "profile_img": user.get_profile_img_url(),
                "isVerified" : user.isVerified,
                "expiry": data.get("expiry"),
                "token" : data.get("token")
            }

            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": basicinfo,
            }

            return Response(response_data)
        except serializers.ValidationError as error:
            return Response({
                "success": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Email or Password",
                "message": error.detail.get('non_field_errors', 'Invalid email or password'),
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    #         # TODO: bila ada email company nanti uncomment
    #         # if user.isVerified is False:
    #         #     return Response({
    #         #     "success": False,
    #         #     "statusCode": status.HTTP_400_BAD_REQUEST,
    #         #     "error": "Bad Request",
    #         #     "message": "User is not verified",
    #         #      }, status=status.HTTP_400_BAD_REQUEST)
    #         # else:
    #         login(request, user)
    #         response_data = {'id': user.id, 'email': user.email}
    #         response_data.update(super().post(request, format=None).data)
   


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
                    send_password_reset_email(request, user)
                    return Response({
                                "success": True,
                                "statusCode": status.HTTP_200_OK,
                                "message": "Password reset email sent",
                            })
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
    
    def get(self, request, *args, **kwargs):
        user = self.request.user

        if user.profile_img:
            profile_img = settings.MEDIA_URL + str(user.profile_img)
        else:
            profile_img = None

        return Response({'profile_img': profile_img})
    
    def put(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.get(request, *args, **kwargs)