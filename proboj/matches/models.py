from django.db import models


class Match(models.Model):
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE)
    configuration = models.ForeignKey("games.Configuration", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class MatchBot(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    bot_version = models.ForeignKey("bots.BotVersion", on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["match", "-score"]
