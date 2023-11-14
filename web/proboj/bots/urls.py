from django.urls import path

from proboj.bots import views

urlpatterns = [
    path("games/<int:game>/bots/", views.BotListView.as_view(), name="bot_list"),
    path(
        "games/<int:game>/bots/<int:pk>/",
        views.BotDetailView.as_view(),
        name="bot_detail",
    ),
    path(
        "games/<int:game>/bots/<int:pk>/versions/create/",
        views.BotUploadView.as_view(),
        name="bot_upload",
    ),
    path(
        "games/<int:game>/bots/<int:bot>/versions/<int:pk>/sources/",
        views.BotDownloadView.as_view(),
        name="bot_download",
    ),
    path(
        "games/<int:game>/bots/<int:bot>/versions/<int:pk>/log/",
        views.BotLogView.as_view(),
        name="bot_compile_log",
    ),
    #
    path(
        "upload/<int:bot>/<secret>/",
        views.CompileUploadView.as_view(),
        name="bot_compile",
    ),
]
