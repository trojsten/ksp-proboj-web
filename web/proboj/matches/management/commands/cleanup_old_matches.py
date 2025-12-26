import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from proboj.games.models import Game
from proboj.matches.models import Match


class Command(BaseCommand):
    help = "Delete old match files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        for game in Game.objects.all():
            matches_to_keep = 10 if game.archived else 100
            matches = Match.objects.filter(game=game).order_by("-created_at")

            old_matches = matches[matches_to_keep:]

            if not old_matches.exists():
                self.stdout.write(f'Game "{game.name}": No old matches to delete')
                continue

            self.stdout.write(
                f'Game "{game.name}": '
                f"Found {old_matches.count()} old matches to delete."
            )

            if dry_run:
                for match in old_matches:
                    self.stdout.write(f"  Would delete match {match.pk}")
                continue

            for match in old_matches:
                self._delete_match_directory(match)
                self.stdout.write(f"  Deleted match {match.pk}")

    def _delete_match_directory(self, match):
        """Delete the entire match directory"""
        match_dir = os.path.join(
            settings.MEDIA_ROOT, f"matches/{match.game_id}/{match.pk}"
        )

        if os.path.exists(match_dir):
            shutil.rmtree(match_dir)
            self.stdout.write(f"  Deleted directory {match_dir}")
