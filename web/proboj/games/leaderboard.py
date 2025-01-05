from collections import defaultdict

from django.core.cache import cache
from django.utils import timezone

from proboj.games.models import Game
from proboj.matches.models import Match, MatchBot


def get_leaderboard(game: Game):
    key = f"leaderboard_{game.id}"
    if key in cache:
        return cache.get(key)

    matches = (
        Match.objects.filter(game=game, finished_at__isnull=False, failed=False)
        .order_by("finished_at")
        .prefetch_related(
            "matchbot_set",
            "matchbot_set__bot_version",
            "matchbot_set__bot_version__bot",
            "matchbot_set__bot_version__bot__user",
        )
    )

    if game.score_reset_at and game.score_reset_at < timezone.now():
        matches = matches.filter(finished_at__gte=game.score_reset_at)

    scores = defaultdict(lambda: 0)
    for match in matches:
        for k in scores.keys():
            scores[k] *= 0.999

        for mbot in match.matchbot_set.all():
            mbot: MatchBot
            if mbot.score is not None:
                scores[mbot.bot_version.bot] += mbot.score

    leaderboard = [(x[0], round(x[1])) for x in scores.items()]
    leaderboard.sort(key=lambda x: -x[1])
    cache.set(key, leaderboard, 60 * 5)
    return leaderboard
