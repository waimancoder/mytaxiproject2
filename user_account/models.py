from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import date
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.validators import FileExtensionValidator
from django.core.files.storage import default_storage
import uuid
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
    email = models.EmailField(_('email address'), unique = True)
    fullname = models.CharField(max_length=125)
    phone_no = models.CharField(max_length = 12)
    isVerified = models.BooleanField(default=False)
    profile_img = models.ImageField(upload_to='profile/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['native_name']


    GENDER_CHOICES =[('male', 'Male'),('female', 'Female')]
    gender = models.CharField(max_length=10,choices=[('male', 'Male'), ('female', 'Female')])
                              
    CHOICES = [('student', 'Student'),('staff', 'Staff'),('outsider', 'Outsider')]
    role = models.CharField(max_length=10,choices=[('student', 'Student'), ('staff', 'Staff'),('outsider', 'Outsider')],)

    class Meta:
            # set the ordering to use the UUID field
        ordering = ['id']

    def get_profile_img_url(self):
        AWS_STORAGE_BUCKET_NAME = 'mytaxi-1'
        AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
        awslocation = os.environ.get('AWS_LOCATION_DEFAULT_PIC')
        if self.profile_img:
            return self.profile_img.url
        return f'https://{AWS_S3_CUSTOM_DOMAIN}/{awslocation}/pic.png'


class StudentID(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricNo = models.CharField(max_length=20, unique=True)
    verification_status = models.BooleanField(default=False)



