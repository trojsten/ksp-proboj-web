import json
import logging
from pathlib import Path

from celery.utils.log import get_task_logger

logger: logging.Logger = get_task_logger(__name__)


def generate_config(match_dir: Path, players: list[dict], timeout: float, logs: bool):
    config = {
        "server": "/server/bin",
        "players": {},
        "timeout": timeout,
        "disable_logs": not logs,
        "game_root": "/match",
    }

    for player in players:
        player_file = (
            Path("/players") / player["name"] / str(player["version"]) / "player"
        )
        player_cmd = str(player_file)
        if player["language"] == "py":
            player_py = player_file.with_suffix(".py")
            player_cmd = f"/usr/bin/python3 {player_py}"

        # todo: start wrapper
        config["players"][player["name"]] = player_cmd

    with (match_dir / "config.json").open("w") as f:
        json.dump(config, f)


def generate_games(match_dir: Path, players: list[dict], args: str):
    games = [
        {
            "gamefolder": "run",
            "players": [p["name"] for p in players],
            "args": args,
        }
    ]

    with (match_dir / "games.json").open("w") as f:
        json.dump(games, f)
