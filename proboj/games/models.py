from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=128)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

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
