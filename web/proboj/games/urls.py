from django.urls import path

from proboj.games.views import AutoPlayView, GameDetailView, HomeView, LeaderboardView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game_detail"),
    path("games/<int:game>/autoplay/", AutoPlayView.as_view(), name="game_autoplay"),
    path(
        "games/<int:game>/leaderboard/",
        LeaderboardView.as_view(),
        name="game_leaderboard",
    ),
]
