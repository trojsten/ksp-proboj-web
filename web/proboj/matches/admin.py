from django.contrib import admin

from proboj.matches.models import Match, MatchBot


class MatchBotInline(admin.TabularInline):
    model = MatchBot


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchBotInline]
