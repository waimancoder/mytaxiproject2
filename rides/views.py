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
from rest_framework import generics, permissions, status, serializers
from .serializers import DriverSerializer
from .models import Driver
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

User = get_user_model()
# Create your views here.
class RequestDriverView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        if user.is_authenticated and not Driver.objects.filter(user=user).exists():
            serializer = DriverSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                driver = serializer.save(user=user)
                return Response({'status': 'success', 'driver': driver.id}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'User must be authenticated and not already registered as a driver.'}, status=status.HTTP_400_BAD_REQUEST)


class DriverApprovalView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        user = request.user
        if user.isVerified and Driver.objects.filter(user=user).exists():
            driver = Driver.objects.get(user=user)
            driver_serializer = DriverSerializer(instance=driver, data=request.data, partial=True)
            if driver_serializer.is_valid():
                driver = driver_serializer.save()
                return Response({'status': 'success', 'driver': driver.id}, status=status.HTTP_200_OK)
            else:
                return Response(driver_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'User must be authenticated and registered as a driver.'}, status=status.HTTP_400_BAD_REQUEST)

def decode_base64_image(base64_string):
    image_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(image_data))


@api_view(['POST'])
def upload_base64_image(request):
    base64_image = request.data.get('image')
    image = decode_base64_image(base64_image)
    
    # Generate a unique filename for the image
    filename = f"{str(uuid.uuid4())}.png"
    
    # Save the image to the server's file system
    image_path = os.path.join("path/to/image/directory", filename)
    with open(image_path, "wb") as image_file:
        image.save(image_file, format="PNG")
        
    # Return a response with the URL of the uploaded image
    image_url = f"https://yourdomain.com/images/{filename}"
    return Response({'status': 'success', 'image_url': image_url})