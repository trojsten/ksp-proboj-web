from django.urls import path

from proboj.bots.views import BotDetailView, BotListView

urlpatterns = [
    path("games/<int:game>/bots/", BotListView.as_view(), name="bot_list"),
    path("games/<int:game>/bots/<int:pk>/", BotDetailView.as_view(), name="bot_detail"),
]
