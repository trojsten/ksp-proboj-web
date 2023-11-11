from django.contrib.auth.views import LoginView as DjLoginView


class LoginView(DjLoginView):
    template_name = "users/login.html"
