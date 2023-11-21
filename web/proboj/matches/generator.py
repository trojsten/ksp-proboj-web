import random
from dataclasses import dataclass

from proboj.bots.models import Bot, BotVersion
from proboj.games.models import Configuration, Game
from proboj.matches.models import Match, MatchBot


@dataclass
class MatchPlan:
    game: Game
    configuration: Configuration
    bots: list[BotVersion]

    def save(self) -> Match:
        match = Match.objects.create(game=self.game, configuration=self.configuration)
        for bot in self.bots:
            MatchBot.objects.create(match=match, bot_version=bot)

        return match

    def to_json(self) -> dict:
        return {
            "players": [f"{bv.bot.name}_v{bv.number}" for bv in self.bots],
            "args": self.configuration.args,
        }


def generate_matches(game: Game, number: int = 1) -> list[MatchPlan]:
    configurations = Configuration.objects.filter(game=game, is_enabled=True).all()
    bots = Bot.objects.filter(game=game, is_enabled=True)
    latest_versions = list(
        BotVersion.objects.filter(bot__in=bots, is_enabled=True)
        .exclude(compiled="")
        .select_related("bot")
        .order_by("bot_id", "-number")
        .distinct("bot_id")
    )
    bot_count = len(latest_versions)

    if bot_count < 2:
        return []

    matches = []
    for i in range(number):
        config: Configuration = random.choice(configurations)
        if config.max_bots and bot_count > config.max_bots:
            bot_count = config.max_bots
        bots: list[BotVersion] = random.sample(latest_versions, k=bot_count)
        matches.append(MatchPlan(game, config, bots))

    return matches
