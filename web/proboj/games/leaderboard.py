from datetime import datetime

from django.db.models import Sum
from django.utils import timezone

from proboj.games.models import Game
from proboj.matches.models import MatchBot


def get_leaderboard(game: Game, until: datetime | None = None):
    bots = MatchBot.objects.filter(
        match__game=game,
        match__is_finished=True,
    )

    if game.score_reset_at and game.score_reset_at < timezone.now():
        bots = bots.filter(match__finished_at__gte=game.score_reset_at)

    if until:
        bots = bots.filter(match__finished_at__lte=until)

    return (
        bots.values("bot_version__bot__name")
        .annotate(total=Sum("score"))
        .order_by("-total")
    )
