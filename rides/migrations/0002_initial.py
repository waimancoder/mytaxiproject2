# Generated by Django 4.1.6 on 2023-03-07 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rides', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='passengers',
            field=models.ManyToManyField(blank=True, related_name='rides', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ride',
            name='passenger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ride',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rides.trip'),
        ),
        migrations.AddField(
            model_name='driver',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='block',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='rides.location'),
        ),
    ]
