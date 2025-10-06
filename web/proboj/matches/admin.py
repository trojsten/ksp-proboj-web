from django.contrib import admin

from proboj.matches.models import Match, MatchBot


class MatchBotInline(admin.TabularInline):
    model = MatchBot

    # select related bot, as it is fetched for each BotVersion
    # (to retrieve BotVersion.__str__) and this is called for every
    # match bot in match admin
    def get_formset(self, request, obj=None, **kwargs):
        formset = super(MatchBotInline, self).get_formset(request, obj, **kwargs)

        queryset = formset.form.base_fields["bot_version"].queryset
        queryset = queryset.select_related("bot")
        formset.form.base_fields["bot_version"].queryset = queryset

        return formset


@admin.action(description="Enqueue selected matches")
def enqueue_match(modeladmin, request, queryset):
    for match in queryset:
        match.enqueue()


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchBotInline]
    actions = [enqueue_match]
