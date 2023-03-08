from django.urls import path, include
from . import views
from rest_framework import routers
from rides.views import DriverIdConfirmationViewSet, LocationDetailView, DriverLicenseViewSet
from django.contrib.auth import get_user_model

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'api/driver/driverlicenses', DriverLicenseViewSet)
router.register(r'api/driver/id-confirmation', DriverIdConfirmationViewSet)

urlpatterns = [
    path('api/locations', LocationDetailView.as_view(), name='location-list'),
    path('api/locations/<str:name>/', LocationDetailView.as_view(), name='location-detail'),
    path('api/driver/driverlicenses/<uuid:user_id>', DriverLicenseViewSet.as_view({'get': 'driver_license_img'}), name='driver_license_img'),
    path('api/driver/id-confirmation/<uuid:user_id>', DriverIdConfirmationViewSet.as_view({'get': 'driver_id_confirmation_img','put': 'update_idConfirm'}), name='driver_id_confirmation_img'),
]

urlpatterns += router.urls
