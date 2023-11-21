from django.contrib import admin

from proboj.matches.models import Match, MatchBot


class MatchBotInline(admin.TabularInline):
    model = MatchBot


@admin.action(description="Enqueue selected matches")
def enqueue_match(modeladmin, request, queryset):
    for match in queryset:
        match.enqueue()


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchBotInline]
    actions = [enqueue_match]
