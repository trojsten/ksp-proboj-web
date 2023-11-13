from django.urls import path

from proboj.bots.views import BotListView

urlpatterns = [
    path("games/<int:game>/bots/", BotListView.as_view(), name="bot_list"),
]
