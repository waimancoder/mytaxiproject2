from django.shortcuts import render
import base64
from io import BytesIO
from PIL import Image
from user_account.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import os 
import uuid 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status, serializers, mixins
from .serializers import DriverSerializer, LocationSerializer
from .models import Driver, Location
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.http import Http404

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
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_data = {'status':"CREATED",'statusCode': status.HTTP_201_CREATED, 'data': serializer.data}
        return Response(response_data, status=status.HTTP_201_CREATED)