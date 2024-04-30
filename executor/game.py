import json
import logging
from pathlib import Path

from celery.utils.log import get_task_logger

logger: logging.Logger = get_task_logger(__name__)


def generate_config(match_dir: Path, players: list[dict], processes_per_player: int, timeout: dict, logs: bool):
    config = {
        "server": "/server/bin",
        "players": {},
        "processes_per_player": processes_per_player,
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
            player_cmd = f"/usr/bin/pypy3 {player_py}"

        wrapper_cmd = (
            f"/home/executor/.local/bin/parent --memory 200000 --processes 1 "
            f"--fs-readonly /usr --fs-readonly {player_file.parent}"
        )
        config["players"][player["name"]] = {
            "command": f"{wrapper_cmd} -- {player_cmd}",
            "language": player["language"],
        }

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
