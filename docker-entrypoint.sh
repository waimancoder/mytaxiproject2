#!/bin/bash

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start Gunicorn and Daphne
exec gunicorn mytaxi.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 60 & \
     daphne mytaxi.asgi:application -b 0.0.0.0 -p 9000
