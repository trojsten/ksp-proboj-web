import os
import secrets

from celery import current_app
from django.conf import settings
from django.core.signing import Signer
from django.db import models
from django.urls import reverse


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
    finished_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    server_log = models.FileField(blank=True, upload_to=_match_server_log)
    observer_log = models.FileField(blank=True, upload_to=_match_observer_log)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Match {self.pk} of {self.game.name}"

    def enqueue(self):
        if self.is_finished:
            return

        if not self.game.server or not self.game.bundle:
            return

        s = Signer()

        server_url = (
            settings.BASE_URL + self.game.server.url + "?v=" + self.game.server_version
        )
        bundle_url = (
            settings.BASE_URL + self.game.bundle.url + "?v=" + self.game.bundle_version
        )

        current_app.send_task(
            "executor.run_match",
            queue="execute",
            kwargs={
                "game_id": self.game_id,
                "server_url": server_url,
                "server_version": self.game.server_version,
                "bundle_url": bundle_url,
                "bundle_version": self.game.bundle_version,
                "players": [
                    {
                        "name": b.bot_version.bot.name,
                        "url": settings.BASE_URL + b.bot_version.compiled.url,
                        "version": b.bot_version.number,
                        "language": b.bot_version.language,
                    }
                    for b in self.matchbot_set.select_related(
                        "bot_version", "bot_version__bot"
                    ).all()
                ],
                "processes_per_player": self.game.processes_per_bot,
                "args": self.configuration.args,
                "report_url": settings.BASE_URL
                + reverse(
                    "match_upload", kwargs={"secret": s.sign_object({"match": self.id})}
                ),
                "timeout": self.game.bot_timeout,
            },
        )


class MatchBot(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    bot_version = models.ForeignKey("bots.BotVersion", on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, null=True)
    log = models.FileField(blank=True, upload_to=_match_bot_log)

    class Meta:
        ordering = ["match", "-score"]

    def __str__(self):
        return f"{self.bot_version.bot.name} in {self.match}"
