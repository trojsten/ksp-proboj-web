from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path
from mozilla_django_oidc.views import OIDCLogoutView

from proboj.users.views import LoginView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
]

if settings.USE_OIDC:
    urlpatterns.append(path("auth/logout/", OIDCLogoutView.as_view(), name="logout"))
else:
    urlpatterns.append(path("auth/logout/", LogoutView.as_view(), name="logout"))
