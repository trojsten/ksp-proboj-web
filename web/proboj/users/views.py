from django.conf import settings
from django.contrib.auth.views import LoginView as DjLoginView
from django.shortcuts import redirect


class LoginView(DjLoginView):
    template_name = "users/login.html"

    def dispatch(self, request, *args, **kwargs):
        if settings.USE_OIDC:
            return redirect("oidc_authentication_init")
        return super().dispatch(request, *args, **kwargs)
