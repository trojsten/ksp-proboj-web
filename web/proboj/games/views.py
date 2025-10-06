import urllib.parse
from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic import DetailView, ListView, TemplateView

from proboj.bots.models import Bot, BotVersion
from proboj.games.leaderboard import get_leaderboard
from proboj.games.mixins import GameMixin
from proboj.games.models import Game, Page
from proboj.matches.models import Match, MatchBot


class HomeView(ListView):
    model = Game
    template_name = "home.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/detail.html"


class GamePageView(GameMixin, DetailView):
    template_name = "games/page.html"

    def get_queryset(self):
        return Page.objects.filter(game=self.game)


class AutoPlayView(GameMixin, TemplateView):
    template_name = "games/autoplay.html"

    def redirect_back(self):
        return HttpResponseRedirect(
            reverse("game_autoplay", kwargs={"game": self.game.id})
            + f"?since={timezone.now().timestamp()}"
        )

    def dispatch(self, request, *args, **kwargs):
        self.ts = self.request.GET.get("since")
        if not self.ts:
            return self.redirect_back()

        try:
            self.ts = make_aware(datetime.fromtimestamp(float(self.ts)))
        except ValueError:
            return self.redirect_back()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        match = (
            Match.objects.filter(game=self.game, finished_at__gt=self.ts)
            .order_by("finished_at")
            .first()
        )
        ctx["match"] = match
        ctx["scores"] = get_leaderboard(self.game)[0:10]

        if match:
            observer_file = match.observer_log.url
            return_url = (
                reverse("game_autoplay", kwargs={"game": self.game.id})
                + f"?since={match.finished_at.timestamp()}"
            )
            ctx["observer"] = (
                f"{settings.OBSERVER_URL}/{self.game.id}/?"
                + urllib.parse.urlencode(
                    {"file": observer_file, "autoplay": "1", "back": return_url}
                )
            )

        return ctx


class LeaderboardView(GameMixin, TemplateView):
    template_name = "games/leaderboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["scores"] = get_leaderboard(self.game)
        ctx["show_profile"] = settings.USE_OIDC
        return ctx


def get_scores_and_timestamps(game, bots, scale=True):
    timestamps = []
    datapoints: dict[int, list[float]] = defaultdict(lambda: [0.0])

    matches = (
        Match.objects.filter(game=game, is_finished=True, failed=False)
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
        )
        .order_by("finished_at")
        .only("finished_at")
    )

    if game.score_reset_at and game.score_reset_at < timezone.now():
        matches = matches.filter(finished_at__gte=game.score_reset_at)

    multiplier = 0.999 if scale else 1

    matches = list(
        matches.values(
            "id",
            "finished_at",
            "matchbot__bot_version__bot_id",
            "matchbot__score",
        )
    )

    last_id = matches[0]["id"]
    timestamps.append(matches[0]["finished_at"].strftime("%Y-%m-%d %H:%M:%S.%f"))

    for match in matches:
        if match["id"] != last_id:
            for bot in bots:
                datapoints[bot.id].append(datapoints[bot.id][-1] * multiplier)
            timestamps.append(match["finished_at"].strftime("%Y-%m-%d %H:%M:%S.%f"))
            last_id = match["id"]

        if match["matchbot__score"] is not None:
            datapoints[match["matchbot__bot_version__bot_id"]][-1] += match[
                "matchbot__score"
            ]

    return datapoints, timestamps


@method_decorator(cache_page(60 * 5), name="dispatch")
class ScoreChartView(GameMixin, View):
    def get(self, request, *args, **kwargs):
        bots = Bot.objects.filter(game=self.game, is_enabled=True).order_by("name")
        datapoints, timestamps = get_scores_and_timestamps(self.game, bots)

        series = []
        for bot in bots:
            series.append(
                {
                    "name": bot.name,
                    "type": "line",
                    "symbol": "none",
                    "data": [
                        [timestamps[i], round(d)]
                        for i, d in enumerate(datapoints[bot.id])
                    ],
                }
            )

        return JsonResponse({"series": series})


@method_decorator(cache_page(60 * 5), name="dispatch")
class ScoreDerivationChartView(GameMixin, View):
    def get(self, request, *args, **kwargs):
        bots = Bot.objects.filter(game=self.game, is_enabled=True).order_by("name")
        datapoints, timestamps = get_scores_and_timestamps(self.game, bots, False)

        diff = 50
        if len(timestamps) <= diff:
            return JsonResponse({"series": []})

        derivations = defaultdict(lambda: [0.0] * diff)
        for bot in datapoints:
            for i in range(diff, len(datapoints[bot])):
                derivations[bot].append(
                    (datapoints[bot][i] - datapoints[bot][i - diff]) / diff
                )

        series = []
        for bot in bots:
            series.append(
                {
                    "name": bot.name,
                    "type": "line",
                    "symbol": "none",
                    "data": [
                        [timestamps[i], round(d, 2)]
                        for i, d in enumerate(derivations[bot.id])
                    ],
                }
            )

        return JsonResponse({"series": series})
