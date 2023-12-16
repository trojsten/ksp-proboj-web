from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from proboj.users.models import User


class TrojstenID(OIDCAuthenticationBackend):
    def get_username(self, claims):
        return claims.get("preferred_username")

    def filter_users_by_claims(self, claims):
        username = self.get_username(claims)
        if not username:
            return User.objects.none()
        return User.objects.filter(username=username)

    def create_user(self, claims):
        user = super().create_user(claims)
        self._update_user(user, claims)
        return user

    def update_user(self, user, claims):
        self._update_user(user, claims)
        return user

    def _update_user(self, user, claims):
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.email = claims.get("email", "")
        user.save()


def logout_url(request):
    return "https://id.trojsten.sk/oauth/logout"
