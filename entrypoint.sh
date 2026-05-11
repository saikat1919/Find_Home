#!/bin/sh
set -e

python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "
from django.contrib.auth.models import User
from home.models import UserProfile
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    u = User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    UserProfile.objects.create(user=u, user_type='admin')
    print('Admin user created.')
else:
    print('Admin user already exists, skipping.')
"
fi

exec gunicorn find_home.wsgi --workers 2 --bind 0.0.0.0:${PORT:-8000}
