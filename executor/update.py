import logging
import zipfile
from io import BytesIO
from pathlib import Path

import requests
from celery.utils.log import get_task_logger

logger: logging.Logger = get_task_logger(__name__)


def update(directory: Path, url: str, version: str, unzip: bool = False):
    directory.mkdir(exist_ok=True, parents=True)
    version_file = directory / "version"
    if version_file.exists() and version_file.read_text() == version:
        logger.debug("Already up-to-date.")
        return

    logger.info("Downloading new version.")
    resp = requests.get(url)
    resp.raise_for_status()
    if not unzip:
        binary = directory / "bin"
        with binary.open("wb") as f:
            f.write(resp.content)
        binary.chmod(0o755)
    else:
        output = directory / "data"
        output.mkdir(exist_ok=True, parents=True)
        with zipfile.ZipFile(BytesIO(resp.content)) as zipf:
            zipf.extractall(output)

    with version_file.open("w") as f:
        f.write(version)


def update_bundle(game_root: Path, bundle_url: str, bundle_version: str):
    logger.debug("Checking bundle version.")
    update(game_root / "bundle", bundle_url, bundle_version, unzip=True)


def update_server(game_root: Path, server_url: str, server_version: str):
    logger.debug("Checking server version.")
    update(game_root / "server", server_url, server_version)


def clean_player_versions(player_dir: Path, version: int):
    pass


def upload_player(game_root: Path, name: str, url: str, version: int, language: str):
    player_dir = game_root / "players" / name
    player_dir.mkdir(exist_ok=True, parents=True)

    ver_dir = player_dir / str(version)
    if ver_dir.exists():
        logger.info(f"Player {player_dir} version {version} is already downloaded.")
        return

    ver_dir.mkdir()
    logger.info(f"Downloading version {version} of {player_dir}")

    resp = requests.get(url)
    resp.raise_for_status()

    if language == "py":
        with zipfile.ZipFile(BytesIO(resp.content)) as zipf:
            zipf.extractall(ver_dir)
    else:
        player_file = ver_dir / "player"
        with player_file.open("wb") as f:
            f.write(resp.content)
        player_file.chmod(0o755)

    clean_player_versions(player_dir, version)
