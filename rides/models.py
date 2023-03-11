from django.db import models
from user_account.models import User
from django.core.validators import FileExtensionValidator
import uuid


class Driver(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle_manufacturer = models.CharField(max_length=128)
    vehicle_model = models.CharField(max_length=128)
    vehicle_color = models.CharField(max_length=128)
    vehicle_registration_number = models.CharField(max_length=128)
    driver_license_id = models.CharField(max_length=128)
    driver_license_img_front = models.ImageField(upload_to='driver-license/front', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    driver_license_img_back = models.ImageField(upload_to='driver-license/back', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    idConfirmation = models.ImageField(upload_to='driver-id-confirmation', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    vehicle_img = models.ImageField(upload_to='driver-vehicle-img', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    isDriverVerified = models.BooleanField(default=False)

    CHOICES =[('owned', 'Owned'),('rented', 'Rented')]
    vehicle_ownership = models.CharField(max_length=20, blank=True,choices=CHOICES)

    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f'{self.user.username} ({self.vehicle_manufacturer} {self.vehicle_model})'
    
class DriverLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} ({self.latitude}, {self.longitude})'


class Trip(models.Model):
    origin = models.CharField(max_length=256, blank=True, null=True)
    destination = models.CharField(max_length=256, blank=True, null=True)
    driver = models.ForeignKey(to=Driver, on_delete=models.CASCADE, related_name='trips', blank=True, null=True)
    passengers = models.ManyToManyField(to=User, blank=True, related_name='rides')
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.driver.username} trip from {self.origin} to {self.destination} [{self.start_time}]'

class Ride(models.Model):
    trip = models.ForeignKey(to=Trip, on_delete=models.CASCADE)
    passenger = models.ForeignKey(to=User, on_delete=models.CASCADE)
    status = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.passenger.username} ride on {self.trip.driver.username} trip [{self.status}]'

class Location(models.Model):
    name = models.CharField(unique=True, max_length=255)
    polygon = models.TextField()
    lat = models.CharField(max_length=255)
    lng = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Block(models.Model):
    name = models.CharField(max_length=255)
    lat = models.CharField(max_length=255)
    lng = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='blocks')

    def __str__(self):
        return self.name

