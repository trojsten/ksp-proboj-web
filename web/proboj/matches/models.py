import os
import secrets

from django.db import models


def _match_path(match: "Match", path: str, filename: str):
    _, ext = os.path.splitext(filename)
    return f"matches/{match.pk}/{path}{ext}"


def _match_server_log(instance: "Match", filename: str):
    return _match_path(instance, "server_log", filename)


def _match_observer_log(instance: "Match", filename: str):
    return _match_path(instance, "observer", filename)


def _match_bot_log(instance: "MatchBot", filename: str):
    return _match_path(
        instance.match,
        f"logs/{instance.bot_version.bot.name}.{secrets.token_hex(16)}",
        filename,
    )


class Match(models.Model):
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE)
    configuration = models.ForeignKey("games.Configuration", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    server_log = models.FileField(blank=True, upload_to=_match_server_log)
    observer_log = models.FileField(blank=True, upload_to=_match_observer_log)

    class Meta:
        ordering = ["-created_at"]


class MatchBot(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    bot_version = models.ForeignKey("bots.BotVersion", on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, null=True)
    log = models.FileField(blank=True, upload_to=_match_bot_log)

    class Meta:
        ordering = ["match", "-score"]
