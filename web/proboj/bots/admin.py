from django.contrib import admin

from proboj.bots.models import Bot, BotVersion


class BotVersionInline(admin.TabularInline):
    model = BotVersion


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    inlines = [BotVersionInline]
    search_fields = ["name"]
    list_display = ["game", "name", "user"]
    list_display_links = ["name"]
    list_filter = ["game__name"]


@admin.register(BotVersion)
class BotVersionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["bot"]
