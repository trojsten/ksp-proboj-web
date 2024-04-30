from pathlib import Path
from zipfile import ZipFile

import requests


def get_log(path: Path) -> Path | None:
    if path.exists():
        return path
    path_txt = path.with_suffix(".txt")
    if path_txt.exists():
        return path_txt
    path_zip = path.with_suffix(".zip")
    if path_zip.exists():
        return path_zip
    path_gz = path.with_suffix(".gz")
    if path_gz.exists():
        return path_gz
    return None


def _add_player_log(zipf: ZipFile, out_dir: Path, player: str, processes_per_player: int):
    if processes_per_player != 1:
        with ZipFile(out_dir / "logs" / f"{player}.zip", "w") as outf:
            for i in range(processes_per_player):
                log = get_log(out_dir / "logs" / f"{player}_{i}")
                if log:
                    outf.write(log, f"{i}{log.suffix}")

    player_log = get_log(out_dir / "logs" / player)
    if player_log:
        zipf.write(player_log, f"{player}{player_log.suffix}")


def report_result(url: str, match_dir: Path, success: bool, players: list[str], processes_per_player: int):
    out_dir = match_dir / "run"

    data = {"successful": success}
    files = {}

    score_file = out_dir / "score.json"
    if score_file.exists():
        with score_file.open() as f:
            data["scores"] = f.read()

    server_log = get_log(out_dir / "logs" / "__server")
    if server_log:
        files["server_log"] = server_log.open("rb")

    observer_log = get_log(out_dir / "observer")
    if observer_log:
        files["observer_log"] = observer_log.open("rb")

    log_zip = out_dir.parent / ".player_logs.zip"
    with ZipFile(log_zip, "w") as zipf:
        for player in players:
            _add_player_log(zipf, out_dir, player, processes_per_player)
    files["bot_logs"] = log_zip.open("rb")

    try:
        resp = requests.post(url, data=data, files=files)
        resp.raise_for_status()
    finally:
        for f in files.values():
            f.close()
