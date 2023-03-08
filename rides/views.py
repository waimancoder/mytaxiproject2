from os import stat
from user_account.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status, serializers, mixins
from .serializers import DriverLicenseSerializer, LocationSerializer
from .models import Driver, Location
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings


User = get_user_model()

class LocationDetailView(generics.RetrieveUpdateAPIView, mixins.ListModelMixin,mixins.CreateModelMixin):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    lookup_field = 'name'

    def get(self, request, *args, **kwargs):
        try:
            if 'name' in kwargs:
                return self.retrieve(request, *args, **kwargs)
            else:
                return self.list(request, *args, **kwargs)
        except Http404:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {'status':"OK",'statusCode': status.HTTP_200_OK, 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {'status':"OK",'statusCode': status.HTTP_200_OK, 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({
                'status': "Bad Request",
                'statusCode': status.HTTP_400_BAD_REQUEST,
                'detail': e.detail
                }
                , status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_data = {
            'status':"CREATED",
            'statusCode': status.HTTP_201_CREATED, 
            'data': serializer.data
            }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_data = {
            'status': "OK",
            'statusCode': status.HTTP_200_OK,
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class DriverLicenseViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverLicenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete','options']
    lookup_field = 'user_id'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = []
        for driver in serializer.data:
            front = driver['driver_license_img_front']
            back = driver['driver_license_img_back']
            if not front:
                front = None
            if not back:
                back = None
            data.append({
                'user_id': driver['user_id'],
                'front': settings.MEDIA_URL + str(front) if front else None,
                'back': settings.MEDIA_URL + str(back) if back else None,
            })
        return Response(data)


    @action(detail=True, methods=['get'])
    def driver_license_img(self, request, user_id=None):
       print("driver_license_img method is called")
       driver = self.get_object()
       front_url = None
       try:
           front_url = settings.MEDIA_URL + str(driver.driver_license_img_front.url)
       except ValueError:
           pass
       back_url = None
       try:
           back_url = settings.MEDIA_URL + str(driver.driver_license_img_back.url)
       except ValueError:
           pass
       data = {
           'user_id': driver.user_id,
           'front': front_url,
           'back': back_url,
       }
       return Response(data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_data = {
        'status': "OK",
        'statusCode': status.HTTP_200_OK,
        'data': serializer.data
            }
        
        return Response(response_data, status=status.HTTP_200_OK)

   


