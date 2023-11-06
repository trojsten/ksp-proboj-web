import os.path
import secrets

from django.conf import settings
from django.core.files.storage import storages
from django.core.validators import validate_slug
from django.db import models
from django.db.models import UniqueConstraint


def private_storage():
    return storages["private"]


def bot_version_path(instance: "BotVersion", filename):
    _, ext = os.path.splitext(filename)
    ts = int(instance.created_at.timestamp())
    return f"bots/{instance.bot_id}/{ts}/{secrets.token_urlsafe(8)}{ext}"


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
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_enabled = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=False)
    sources = models.FileField(
        upload_to=bot_version_path, storage=private_storage, blank=True, null=True
    )
    compiled = models.FileField(
        upload_to=bot_version_path, storage=private_storage, blank=True, null=True
    )

    number = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        timestamp = self.created_at.strftime("%d.%m.%Y %H:%M:%S")
        return f"{self.bot} {timestamp}"

    def save(self, **kwargs):
        if self.number is None:
            last_version = (
                BotVersion.objects.filter(bot=self.bot).order_by("-number").first()
            )
            self.number = last_version.number if last_version else 1
        return super().save(**kwargs)
