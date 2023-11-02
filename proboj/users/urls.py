from django.urls import path

from proboj.users.views import LoginView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
]
