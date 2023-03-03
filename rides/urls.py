from django.urls import path
from . import views
from .views import LocationDetailView
from django.contrib.auth import get_user_model

urlpatterns = [
    path('api/locations', LocationDetailView.as_view(), name='location-list'),
    path('api/locations/<str:name>/', LocationDetailView.as_view(), name='location-detail')
]
