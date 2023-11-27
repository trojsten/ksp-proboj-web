from pathlib import Path
from zipfile import ZipFile

import requests


def get_log(path: Path) -> Path | None:
    if path.exists():
        return path
    path_txt = path.with_suffix(".txt")
    if path_txt.exists():
        return path_txt
    path_gz = path.with_suffix(".gz")
    if path_gz.exists():
        return path_gz
    return None


def report_result(url: str, match_dir: Path, success: bool, players: list[str]):
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

    zipf = ZipFile(out_dir / ".player_logs.zip", "w")
    for player in players:
        player_log = get_log(out_dir / "logs" / player)
        if player_log:
            zipf.write(player_log, f"{player}{player_log.suffix}")
    files["bot_logs"] = zipf

    try:
        resp = requests.post(url, data=data, files=files)
        resp.raise_for_status()
    finally:
        for f in files.values():
            f.close()
