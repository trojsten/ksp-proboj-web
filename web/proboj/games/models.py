import os

from django.db import models

from proboj.storage import OverwriteStorage


def _game_path(instance: "Game", path: str, filename: str):
    _, ext = os.path.splitext(filename)
    return f"game/{instance.id}/{path}{ext}"


def _game_server(instance: "Game", filename: str):
    return _game_path(instance, "server", filename)


def _game_bundle(instance: "Game", filename: str):
    return _game_path(instance, "bundle", filename)


class Game(models.Model):
    name = models.CharField(max_length=128)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    server = models.FileField(
        storage=OverwriteStorage(), upload_to=_game_server, blank=True
    )
    server_version = models.CharField(max_length=64, blank=True)
    bundle = models.FileField(
        storage=OverwriteStorage(), upload_to=_game_bundle, blank=True
    )
    bundle_version = models.CharField(max_length=64, blank=True)

    bot_timeout = models.DecimalField(max_digits=6, decimal_places=3, default=1)
    auto_play = models.IntegerField(default=0)
    max_bots = models.IntegerField(default=0)

    rules = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_at", "-end_at"]

    def __str__(self):
        return self.name


class Configuration(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    args = models.TextField(blank=True)
    max_bots = models.IntegerField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["game", "name"]

    def __str__(self):
        return self.name
