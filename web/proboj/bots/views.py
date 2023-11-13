from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from proboj.bots.models import Bot
from proboj.games.mixins import GameMixin


class BotQuerySetMixin:
    def get_queryset(self):
        return Bot.objects.filter(game=self.game, user=self.request.user)


class BotListView(LoginRequiredMixin, BotQuerySetMixin, GameMixin, ListView):
    template_name = "bots/list.html"


class BotDetailView(LoginRequiredMixin, BotQuerySetMixin, GameMixin, DetailView):
    template_name = "bots/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["versions"] = self.object.botversion_set.all()
        return ctx
