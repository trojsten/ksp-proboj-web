from collections import defaultdict

from django.core.cache import cache
from django.db.models import Prefetch
from django.utils import timezone

from proboj.bots.models import Bot, BotVersion
from proboj.games.models import Game
from proboj.matches.models import Match, MatchBot
from proboj.users.models import User


def get_leaderboard(game: Game):
    key = f"leaderboard_{game.id}"
    if key in cache:
        return cache.get(key)

    matches = (
        Match.objects.filter(game=game, finished_at__isnull=False, failed=False)
        .order_by("finished_at")
        .prefetch_related(
            Prefetch(
                "matchbot_set",
                queryset=MatchBot.objects.filter(score__gt=0)
                .order_by()
                .only("score", "match_id", "bot_version"),
            ),
            Prefetch(
                "matchbot_set__bot_version",
                queryset=BotVersion.objects.filter().order_by().only("bot_id"),
            ),
            Prefetch(
                "matchbot_set__bot_version__bot",
                queryset=Bot.objects.filter().order_by().only("name", "user_id"),
            ),
            Prefetch(
                "matchbot_set__bot_version__bot__user",
                queryset=User.objects.filter()
                .order_by()
                .only("username", "first_name", "last_name"),
            ),
        )
    )

    if game.score_reset_at and game.score_reset_at < timezone.now():
        matches = matches.filter(finished_at__gte=game.score_reset_at)

    matches = list(
        matches.values_list(
            "id",
            "matchbot__bot_version__bot_id",
            "matchbot__score",
            "matchbot__bot_version__bot__name",
            "matchbot__bot_version__bot__user__username",
            "matchbot__bot_version__bot__user__first_name",
            "matchbot__bot_version__bot__user__last_name",
        )
    )

    scores = defaultdict(lambda: 0.0)
    bots = {}

    last_id = matches[0][0]

    for match in matches:
        if match[0] != last_id:
            last_id = match[0]
            for k in scores.keys():
                scores[k] *= 0.999

        if match[2] is not None:
            if match[1] not in bots:
                bots[match[1]] = {
                    "name": match[3],
                    "user": {
                        "username": match[4],
                        "first_name": match[5],
                        "last_name": match[6],
                    },
                }

            scores[match[1]] += match[2]

    leaderboard = [(bots[x[0]], round(x[1])) for x in scores.items()]
    leaderboard.sort(key=lambda x: -x[1])
    cache.set(key, leaderboard, 60 * 5)
    return leaderboard
