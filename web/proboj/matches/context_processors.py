from django.conf import settings


def observer_url(request):
    return {
        "OBSERVER_URL": settings.OBSERVER_URL,
    }
