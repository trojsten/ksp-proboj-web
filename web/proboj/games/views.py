import urllib.parse
from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.generic import DetailView, ListView, TemplateView

from proboj.games.leaderboard import get_leaderboard
from proboj.games.mixins import GameMixin
from proboj.games.models import Game
from proboj.matches.models import Match


class HomeView(ListView):
    model = Game
    template_name = "home.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/detail.html"


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
        ctx["scores"] = get_leaderboard(self.game, self.ts)[0:10]

        if match:
            observer_file = match.observer_log.url
            return_url = (
                reverse("game_autoplay", kwargs={"game": self.game.id})
                + f"?since={match.finished_at.timestamp()}"
            )
            ctx[
                "observer"
            ] = f"{settings.OBSERVER_URL}/{self.game.id}/?" + urllib.parse.urlencode(
                {"file": observer_file, "autoplay": "1", "back": return_url}
            )

        return ctx


class LeaderboardView(GameMixin, TemplateView):
    template_name = "games/leaderboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["scores"] = get_leaderboard(self.game)
        return ctx
