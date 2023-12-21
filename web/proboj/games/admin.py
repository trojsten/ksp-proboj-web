from django.contrib import admin

from proboj.games.models import Configuration, Game, Page


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["name", "start_at", "end_at"]
    search_fields = ["name"]


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ["game", "name", "max_bots", "is_enabled"]
    search_fields = ["name"]
    list_display_links = ["name"]
    list_filter = ["game__name"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["game", "name", "slug"]
    search_fields = ["name"]
    list_display_links = ["name"]
