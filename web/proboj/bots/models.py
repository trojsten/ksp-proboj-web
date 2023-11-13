import os.path
import secrets

from celery import current_app
from django.conf import settings
from django.core.validators import validate_slug
from django.db import models
from django.db.models import UniqueConstraint


def _bot_version_path(instance: "BotVersion", filename, destname):
    _, ext = os.path.splitext(filename)
    return f"bots/{instance.bot_id}/{instance.secret}/{destname}{ext}"


def bot_version_sources(instance: "BotVersion", filename):
    return _bot_version_path(instance, filename, "sources")


def bot_version_compiled(instance: "BotVersion", filename):
    return _bot_version_path(instance, filename, "compiled")


def bot_secret():
    return secrets.token_hex(16)


class Bot(models.Model):
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, validators=[validate_slug])
    is_enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [UniqueConstraint("game", "name", name="bot__unique_name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class BotVersion(models.Model):
    class Language(models.TextChoices):
        PYTHON = ("py", "Python")
        CPP = ("cpp", "C++")

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    secret = models.CharField(max_length=32, default=bot_secret)

    is_enabled = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=False)

    language = models.CharField(choices=Language.choices)
    sources = models.FileField(upload_to=bot_version_sources, blank=True, null=True)
    compiled = models.FileField(upload_to=bot_version_compiled, blank=True, null=True)
    compile_log = models.TextField(blank=True)

    number = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint("bot", "secret", name="botversion__bot_secret__unique"),
        ]

    def __str__(self):
        return f"{self.bot} v{self.number}"

    def compile(self):
        if self.language == BotVersion.Language.PYTHON:
            self.compiled = self.sources
            self.save()
            return

        current_app.send_task(
            "compiler.compile_player",
            queue="compile",
            kwargs={
                "source_url": self.sources.url,
                "language": self.language.value,
                "report_url": "",
            },
        )

    def save(self, **kwargs):
        if self.number is None:
            last_version = (
                BotVersion.objects.filter(bot=self.bot).order_by("-number").first()
            )
            self.number = last_version.number if last_version else 1
        return super().save(**kwargs)
