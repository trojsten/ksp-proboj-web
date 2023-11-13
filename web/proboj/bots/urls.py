from django.urls import path

from proboj.bots.views import (
    BotDetailView,
    BotListView,
    BotUploadView,
    CompileUploadView,
)

urlpatterns = [
    path("games/<int:game>/bots/", BotListView.as_view(), name="bot_list"),
    path("games/<int:game>/bots/<int:pk>/", BotDetailView.as_view(), name="bot_detail"),
    path(
        "games/<int:game>/bots/<int:pk>/versions/create/",
        BotUploadView.as_view(),
        name="bot_upload",
    ),
    path("upload/<int:bot>/<secret>/", CompileUploadView.as_view(), name="bot_compile"),
]
