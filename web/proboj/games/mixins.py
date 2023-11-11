from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from proboj.games.models import Game


class GameMixin:
    @cached_property
    def game(self):
        return get_object_or_404(Game, id=self.kwargs["game"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["game"] = self.game
        return ctx
