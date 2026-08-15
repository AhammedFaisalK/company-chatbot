#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Ensuring superuser exists..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created.')
else:
    print('Superuser already exists or env vars not set — skipping.')
"

echo "Ingesting knowledge base..."
python manage.py ingest_knowledge

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 120