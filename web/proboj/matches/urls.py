from django.urls import path

from proboj.matches.views import MatchDetailView, MatchListView

urlpatterns = [
    path("games/<int:game>/matches/", MatchListView.as_view(), name="match_list"),
    path(
        "games/<int:game>/matches/<int:pk>/",
        MatchDetailView.as_view(),
        name="match_detail",
    ),
]
