from django.shortcuts import render
from rest_framework import generics, permissions, status
from .serializers import UserSerializer, AuthTokenSerializer, RegisterSerializer, StudentIDVerificationSerializer
from django.shortcuts import render
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import login, get_user_model
from rest_framework.views import APIView
from .models import StudentID
from django.contrib.auth.tokens import default_token_generator as auth_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from mytaxi import settings
from rest_framework.decorators import api_view



# Create your views here.
class UserRetrieveAPIView(generics.RetrieveAPIView):
    User =get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        current_site = get_current_site(request)
        subject = 'Verify your email address'
        message = render_to_string('verification_email.html', {
            'user': user,
            'native_name': user.native_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': auth_token_generator.make_token(user),
        })
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email])

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


class StudentIDVerificationView(APIView):
    # serializer_class = StudentIDVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = StudentIDVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_number = serializer.validated_data['id_number']
        try:
            if StudentID.objects.get(user=request.user).DoesNotExist or StudentID.objects.get(id_number=id_number).DoesNotExist:
                return Response({'status': 'User already has a Student ID'})

        except StudentID.DoesNotExist:
            student = StudentID.objects.create(user= request.user, id_number=id_number, verification_status=True)
            student.save()
            request.user.isVerified = True
            request.user.save()
            return Response({'status': 'ID Verified'})


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
        return Response('Your email address has been verified.')
    else:
        return Response('Verification link is invalid!')
