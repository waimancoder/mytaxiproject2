# Generated by Django 4.1.6 on 2023-03-08 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0002_rename_id_number_studentid_matricno'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
