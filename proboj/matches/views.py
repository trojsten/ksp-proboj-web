from django.views.generic import DetailView, ListView

from proboj.games.mixins import GameMixin
from proboj.matches.models import Match


class MatchListView(GameMixin, ListView):
    template_name = "matches/list.html"

    def get_queryset(self):
        return (
            Match.objects.filter(game=self.game)
            .order_by("-created_at")
            .select_related("configuration")
            .prefetch_related("matchbot_set", "matchbot_set__bot_version__bot")
        )


class MatchDetailView(GameMixin, DetailView):
    template_name = "matches/detail.html"

    def get_queryset(self):
        return Match.objects.filter(game=self.game).prefetch_related(
            "matchbot_set", "matchbot_set__bot_version__bot"
        )
