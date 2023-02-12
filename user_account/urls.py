from django.urls import path
from knox import views as knox_views
from . import views
from .views import RegisterAPI, LoginAPI, StudentIDVerificationView, UserRetrieveAPIView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model

User = get_user_model()

urlpatterns = [
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/users/<int:pk>', UserRetrieveAPIView().as_view(), name='retrieveuser'),
    path('api/studentverification/', StudentIDVerificationView.as_view(), name='studentverification'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify-email'),
    
]