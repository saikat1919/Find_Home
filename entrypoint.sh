#!/bin/sh
set -e

python manage.py migrate --noinput
exec gunicorn find_home.wsgi --workers 2 --bind 0.0.0.0:${PORT:-8000}
