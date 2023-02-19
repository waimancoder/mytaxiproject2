from django.urls import path
from . import views
from .views import RequestDriverView, DriverApprovalView
from django.contrib.auth import get_user_model

urlpatterns = [
    path('api/requestdriver', RequestDriverView.as_view(), name='requestdriver'),
    path('api/driverapproval', DriverApprovalView.as_view(), name='driverapproval'),
]
