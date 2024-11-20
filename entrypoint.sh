#!/bin/bash
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py docker_start
gunicorn core.wsgi:application --bind 0.0.0.0:8000
