import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proboj.settings")

app = Celery("proboj")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "enqueue-matches": {
        "task": "proboj.matches.tasks.enqueue_matches",
        "schedule": 15.0,
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
