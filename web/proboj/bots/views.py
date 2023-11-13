from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from proboj.bots.models import Bot
from proboj.games.mixins import GameMixin


class BotListView(LoginRequiredMixin, GameMixin, ListView):
    template_name = "bots/list.html"

    def get_queryset(self):
        return Bot.objects.filter(game=self.game, user=self.request.user)
