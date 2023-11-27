#!/bin/bash
set -euo pipefail

mode="${1:-prod}"

if [ "$mode" = "worker" ]; then
  exec celery -A proboj.celery worker -c 2
elif [ "$mode" = "beat" ]; then
  exec celery -A proboj.celery beat
fi

#python manage.py wait_for_database
python manage.py migrate

pygmentize -S monokai -f html -a .codehilite > /app/proboj/theme/static/code.css

if [ "$mode" = "dev" ]; then
	exec python manage.py runserver 0.0.0.0:8000
else
	python manage.py collectstatic --no-input
	exec gunicorn -b 0.0.0.0:8000 proboj.wsgi:application
fi
