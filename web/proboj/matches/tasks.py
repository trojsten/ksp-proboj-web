from datetime import timedelta

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


@shared_task
def delete_old_matches():
    games = Game.objects.all()
    for game in games:
        last_match = (
            Match.objects.filter(game=game, finished_at__isnull=False)
            .order_by("-finished_at")
            .first()
        )
        if not last_match:
            continue

        older_than_week = Match.objects.filter(
            game=game, finished_at__lte=last_match.finished_at - timedelta(days=7)
        ).prefetch_related("matchbot_set")
        for match in older_than_week:
            if match.server_log:
                match.server_log.delete()

            for bot in match.matchbot_set.all():
                if bot.log:
                    bot.log.delete()

        older_than_month = Match.objects.filter(
            game=game, finished_at__lte=last_match.finished_at - timedelta(days=30)
        )
        for match in older_than_month:
            if match.observer_log:
                match.observer_log.delete()
