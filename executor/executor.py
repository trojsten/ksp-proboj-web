import logging
import tempfile
from pathlib import Path

import yaml
from celery import Celery
from celery.utils.log import get_task_logger
from filelock import FileLock

from game import generate_config, generate_games
from report import report_result
from run import start_match
from update import update_bundle, update_server, upload_player

logger: logging.Logger = get_task_logger(__name__)

with open("config.yml") as f:
    CONFIG: dict = yaml.safe_load(f)

app = Celery(__name__)
app.conf.broker_connection_retry = False
app.conf.broker_connection_retry_on_startup = True
app.config_from_object(CONFIG["celery"])


@app.task(bind=True)
def run_match(
    self,
    game_id: int,
    server_url: str,
    server_version: str,
    bundle_url: str,
    bundle_version: str,
    players: list[dict],
    processes_per_player: int,
    args: str,
    report_url: str,
    timeout: dict,
):
    game_root = Path(CONFIG["executor"]["root"]) / str(game_id)
    lock_root = Path(CONFIG["executor"]["root"]) / "locks"
    lock = FileLock(game_root / ".lock", timeout=-1)
    logger.info(f"Locking game {game_id} for update.")
    lock.acquire()

    try:
        update_server(game_root, server_url, server_version)

        if bundle_url:
            update_bundle(game_root, bundle_url, bundle_version)

        for player in players:
            upload_player(
                game_root,
                player["name"],
                player["url"],
                player["version"],
                player["language"],
            )
    except Exception as e:
        self.retry(exc=e)
    finally:
        logger.info(f"Unlocking game {game_id}.")
        lock.release()

    with tempfile.TemporaryDirectory(prefix="proboj_executor_") as match_dir:
        match_dir = Path(match_dir)
        generate_config(match_dir, players, processes_per_player, timeout, CONFIG["executor"]["logs"])
        generate_games(match_dir, players, args)

        successful = False
        try:
            start_match(
                CONFIG["podman"]["url"],
                CONFIG["executor"]["image"],
                match_dir,
                game_root,
                lock_root,
                CONFIG["executor"]["pin_cpu"],
            )
            successful = True
        except Exception as e:
            logger.error(f"Match did not end well: {e}")

        try:
            report_result(
                report_url, match_dir, successful, [pl["name"] for pl in players]
            )
        except Exception as e:
            self.retry(exc=e)
