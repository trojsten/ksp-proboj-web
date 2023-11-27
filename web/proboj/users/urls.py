from django.contrib.auth.views import LogoutView
from django.urls import path

from proboj.users.views import LoginView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
