from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from proboj.bots.models import Bot
from proboj.games.mixins import GameMixin


class BotQuerySetMixin:
    def get_queryset(self):
        return Bot.objects.filter(game=self.game, user=self.request.user)


class BotMixin(GameMixin):
    @cached_property
    def bot(self):
        return get_object_or_404(
            Bot.objects.filter(game=self.game, user=self.request.user),
            id=self.kwargs["bot"],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["bot"] = self.bot
        return ctx
