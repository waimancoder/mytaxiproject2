from django.conf.urls import handler404
from django.urls import path
from knox import views as knox_views
from . import views
from .views import RegisterAPI, LoginAPI, UserRetrieveAPIView, PasswordResetView, PasswordResetConfirmView, ProfilePictureView
from .views import UserUpdateAPI, UserListView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from rest_framework import routers


User = get_user_model()
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'api/users', UserRetrieveAPIView, basename='users')

urlpatterns = [
    path('api/login', LoginAPI.as_view(), name='login'),
    path('api/logout', knox_views.LogoutView.as_view(), name='logout'),
    path('api/register', RegisterAPI.as_view(), name='register'),
    # path('api/studentverification', StudentIDVerificationView.as_view(), name='studentverification'),
    path('api/verify-email/<str:uidb64>/<str:token>', views.verify_email, name='verify-email'),
    path('api/password_reset', PasswordResetView.as_view(), name='password_reset'),
    path('api/password_reset_confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/userupdate/<str:email>', UserUpdateAPI.as_view(), name='userupdate'),
    path('api/userlist', UserListView.as_view(), name='userlist'),
    path('api/profile-pic', ProfilePictureView.as_view(), name='profile-pic'),

    
]

urlpatterns += router.urls