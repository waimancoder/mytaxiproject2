from django.urls import path
from . import views
from .views import RequestDriverView, DriverApprovalView, LocationDetailView
from django.contrib.auth import get_user_model

urlpatterns = [
    path('api/requestdriver', RequestDriverView.as_view(), name='requestdriver'),
    path('api/driverapproval', DriverApprovalView.as_view(), name='driverapproval'),
    path('api/locations', LocationDetailView.as_view(), name='location-list'),
    path('api/locations/(?P<name>[\w\s]+)/$', LocationDetailView.as_view(), name='location-detail')

]
