from django.contrib import admin

from proboj.games.models import Configuration, Game


class ConfigurationInline(admin.StackedInline):
    model = Configuration


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [ConfigurationInline]
    list_display = ["name", "start_at", "end_at"]
    search_fields = ["name"]
