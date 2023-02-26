from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import date

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
    email = models.EmailField(_('email address'), unique = True)
    native_name = models.CharField(max_length=125)
    phone_no = models.CharField(max_length = 12)
    isVerified = models.BooleanField(default=False)
    profile_img = models.CharField(max_length=1000000,null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['native_name']

    CHOICES = [('student', 'Student'),('staff', 'Staff'),('outsider', 'Outsider')]
    role = models.CharField(max_length=10,choices=[('student', 'Student'), ('staff', 'Staff'),('outsider', 'Outsider')],)


class StudentID(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    verification_status = models.BooleanField(default=False)



