from django.db import models
from user_account.models import User


class Driver(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    car_make = models.CharField(max_length=128)
    car_model = models.CharField(max_length=128)
    car_registration_number = models.CharField(max_length=128)
    driver_license_id = models.CharField(max_length=128)
    driver_license_img = models.CharField(max_length=1000000)
    isDriverVerified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} ({self.car_make} {self.car_model})'

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


