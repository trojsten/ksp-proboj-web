from django.views.generic import DetailView, ListView

from proboj.games.models import Game


class HomeView(ListView):
    model = Game
    template_name = "home.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/detail.html"
