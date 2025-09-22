from pathlib import Path

from environ import Env

env = Env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-airootheesaethahpoo2EeLahze3wooGh9Ash2zae9ohgiengi",
)
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])
BASE_URL = env("BASE_URL")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "proboj.theme",
    "proboj.users",
    "proboj.games",
    "proboj.bots",
    "proboj.matches",
    #
    "django_probes",
    "widget_tweaks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "proboj.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "proboj.matches.context_processors.observer_url",
            ],
        },
    },
]

WSGI_APPLICATION = "proboj.wsgi.application"

DATABASES = {"default": env.db()}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_CACHE_URL", default=env("CELERY_BROKER_URL")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = "users.User"
LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "login"

USE_OIDC = env("PROBOJ_USE_OIDC", default=False)
if USE_OIDC:
    AUTHENTICATION_BACKENDS = [
        "proboj.users.oidc.TrojstenID",
        "django.contrib.auth.backends.ModelBackend",
    ]

    MIDDLEWARE.append("mozilla_django_oidc.middleware.SessionRefresh")
    INSTALLED_APPS.append("mozilla_django_oidc")

    OIDC_OP_AUTHORIZATION_ENDPOINT = env(
        "OIDC_OP_AUTHORIZATION_ENDPOINT",
        default="https://id.trojsten.sk/oauth/authorize/",
    )
    OIDC_OP_USER_ENDPOINT = env(
        "OIDC_OP_USER_ENDPOINT", default="https://id.trojsten.sk/oauth/userinfo/"
    )
    OIDC_OP_TOKEN_ENDPOINT = env(
        "OIDC_OP_TOKEN_ENDPOINT", default="https://id.trojsten.sk/oauth/token/"
    )
    OIDC_RP_SCOPES = "openid email profile"
    OIDC_RP_SIGN_ALGO = "HS256"
    OIDC_RP_CLIENT_ID = env("OIDC_RP_CLIENT_ID")
    OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET")
    OIDC_OP_LOGOUT_URL_METHOD = "proboj.users.oidc.logout_url"
    OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 60 * 60 * 12

LANGUAGE_CODE = "sk"
TIME_ZONE = "Europe/Bratislava"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "uploads/"
MEDIA_ROOT = BASE_DIR / "uploads"

OBSERVER_URL = "/observer"
OBSERVER_ROOT = BASE_DIR / "observer"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
