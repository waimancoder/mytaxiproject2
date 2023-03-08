from django.urls import path, include
from . import views
from rest_framework import routers
from rides.views import LocationDetailView, DriverLicenseViewSet
from django.contrib.auth import get_user_model

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'api/driver/driverlicenses', DriverLicenseViewSet)

urlpatterns = [
    path('api/locations', LocationDetailView.as_view(), name='location-list'),
    path('api/locations/<str:name>/', LocationDetailView.as_view(), name='location-detail'),
    path('api/driver/driverlicenses/<uuid:user_id>', DriverLicenseViewSet.as_view({'get': 'driver_license_img'}), name='driver_license_img'),
]

urlpatterns += router.urls
