from django.urls import path

from proboj.games.views import GameDetailView, HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game_detail"),
]
