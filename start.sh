#!/bin/bash
set -euo pipefail

mode="${1:-prod}"

#python manage.py wait_for_database
python manage.py migrate

if [ "$mode" = "dev" ]; then
	exec python manage.py runserver 0.0.0.0:8000
else
	python manage.py collectstatic --no-input
	exec gunicorn -b 0.0.0.0:8000 proboj.wsgi:app
fi
