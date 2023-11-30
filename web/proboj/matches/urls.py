from django.urls import path

from proboj.matches.views import (
    MatchConfigView,
    MatchDetailView,
    MatchListView,
    MatchUploadView,
)

urlpatterns = [
    path("games/<int:game>/matches/", MatchListView.as_view(), name="match_list"),
    path(
        "games/<int:game>/matches/<int:pk>/",
        MatchDetailView.as_view(),
        name="match_detail",
    ),
    path(
        "games/<int:game>/matches.json",
        MatchConfigView.as_view(),
        name="match_config",
    ),
    path("api/match_upload/<secret>/", MatchUploadView.as_view(), name="match_upload"),
]
