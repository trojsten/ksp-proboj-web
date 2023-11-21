from celery import shared_task

from proboj.games.models import Game
from proboj.matches.generator import generate_matches
from proboj.matches.models import Match


@shared_task
def enqueue_matches():
    games = Game.objects.filter(auto_play__gt=0).all()
    for game in games:
        pending_matches = Match.objects.filter(game=game, is_finished=False).count()
        create_matches = game.auto_play - pending_matches

        if create_matches <= 0:
            continue

        plans = generate_matches(game, create_matches)
        for plan in plans:
            match = plan.save()
            match.enqueue()
