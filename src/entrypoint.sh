#!/usr/bin/env bash

until nc -z db 3306; do
    >&2 echo "mysql is unavailable - sleeping"
    sleep 1
done
>&2 echo "mysql is up - executing command"

python manage.py collectstatic --no-input
python manage.py migrate
#gunicorn labmine.wsgi:application --bind 0.0.0.0:8000
uwsgi --socket :8001 --module labmine.wsgi --py-autoreload 1 --logto /tmp/mylog.log