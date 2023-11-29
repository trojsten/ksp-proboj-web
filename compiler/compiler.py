import logging
import tempfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests
import yaml
from celery import Celery
from celery.utils.log import get_task_logger
from podman import PodmanClient
from requests import HTTPError

logger: logging.Logger = get_task_logger(__name__)

with open("config.yml") as f:
    CONFIG: dict = yaml.safe_load(f)

app = Celery(__name__, broker=CONFIG["celery"]["broker"])
app.conf.broker_connection_retry = False
app.conf.broker_connection_retry_on_startup = True
app.config_from_object(CONFIG["celery"])


@dataclass
class Result:
    successful: bool
    log: str
    output: Path | None = None


@dataclass
class CompilerOutput:
    exitcode: int
    log: str


@app.task(time_limit=60, autoretry_for=(HTTPError,))
def compile_player(source_url: str, language: str, report_url: str):
    if language not in CONFIG["images"]:
        report_failure(report_url, f"Unknown language '{language}'.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        player_output = tmpdir_path / "player"

        src = download_sources(source_url)
        unzip_sources(src, tmpdir_path)
        if player_output.exists():
            report_failure(report_url, "File 'player' already exists.")
            return

        try:
            result = compile_sources(tmpdir_path, language)
        except Exception as e:
            report_failure(report_url, str(e))
            return

        if not player_output.exists():
            report_failure(report_url, "Compiler did not produce output.", result.log)
            return

        report_result(
            report_url,
            Result(
                result.exitcode == 0,
                result.log,
                player_output,
            ),
        )


def download_sources(url: str) -> BytesIO:
    logger.info(f"Downloading sources ZIP from {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BytesIO(resp.content)


def unzip_sources(zipf: BytesIO, dest: Path) -> None:
    logger.info("Extracting source archive")
    with ZipFile(zipf, "r") as zipf:
        zipf.extractall(dest)


def compile_sources(dir: Path, language: str) -> CompilerOutput:
    with PodmanClient(base_url=CONFIG["podman"]["url"]) as podman:
        container = podman.containers.create(
            image=CONFIG["images"][language],
            mounts=[
                {
                    "type": "bind",
                    "source": str(dir.absolute()),
                    "target": "/data",
                    "read_only": False,
                }
            ],
            network_mode="none",
            userns_mode="keep-id",
        )

        exitcode = -1
        logs = ""

        try:
            container.start()
            container.wait(condition="exited")

            logs = container.logs(stderr=True)
            if isinstance(logs, bytes):
                logs = logs.decode()
            else:
                logs = "".join([r.decode() for r in logs])

            inspect = container.inspect()
            exitcode = inspect["State"]["ExitCode"]
        except Exception as e:
            logs += f"\nINTERNAL ERROR: {e}\n"
        finally:
            container.remove()

        return CompilerOutput(exitcode, logs)


def report_result(url: str, res: Result) -> None:
    data = {
        "successful": res.successful,
        "log": res.log,
    }
    files = {}

    if res.output:
        files["output"] = res.output.open("rb")

    try:
        resp = requests.post(url, data=data, files=files)
        resp.raise_for_status()
    finally:
        if res.output:
            files["output"].close()


def report_failure(url: str, error: str, log: str | None = None):
    if log:
        log += f"\nINTERNAL ERROR: {error}\n"
    else:
        log = f"INTERNAL ERROR: {error}\n"

    logger.error(f"Could not compile: {error}")
    report_result(url, Result(False, log))
