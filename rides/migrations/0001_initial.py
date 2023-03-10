# Generated by Django 4.1.6 on 2023-03-07 12:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('lat', models.CharField(max_length=255)),
                ('lng', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('vehicle_manufacturer', models.CharField(max_length=128)),
                ('vehicle_model', models.CharField(max_length=128)),
                ('vehicle_color', models.CharField(max_length=128)),
                ('vehicle_ownership', models.CharField(max_length=128)),
                ('vehicle_registration_number', models.CharField(max_length=128)),
                ('driver_license_id', models.CharField(max_length=128)),
                ('driver_license_img_front', models.ImageField(blank=True, null=True, upload_to='driver-license/back', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])])),
                ('idConfirmation', models.ImageField(blank=True, null=True, upload_to='driver-id-confirmation', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])])),
                ('vehicle_img', models.ImageField(blank=True, null=True, upload_to='driver-vehicle-img', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])])),
                ('isDriverVerified', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('polygon', models.TextField()),
                ('lat', models.CharField(max_length=255)),
                ('lng', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', models.CharField(blank=True, max_length=256, null=True)),
                ('destination', models.CharField(blank=True, max_length=256, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trips', to='rides.driver')),
            ],
        ),
    ]
