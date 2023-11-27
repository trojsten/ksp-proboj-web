from django.urls import path

from proboj.games.views import AutoPlayView, GameDetailView, HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game_detail"),
    path("games/<int:game>/autoplay/", AutoPlayView.as_view(), name="game_autoplay"),
]
