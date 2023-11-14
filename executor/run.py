import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

from filelock import FileLock, Timeout
from podman import PodmanClient

from celery.utils.log import get_task_logger

logger: logging.Logger = get_task_logger(__name__)


@dataclass
class CPULock:
    cpu: int
    lock: FileLock


def select_cpu(lock_root: Path) -> CPULock:
    logger.debug("Acquiring lock for a CPU core.")
    while True:
        for i in range(os.cpu_count()):
            fl = FileLock(lock_root / str(i))
            try:
                fl.acquire(blocking=False)
                logger.info(f"Acquired lock for CPU {i}.")
                return CPULock(i, fl)
            except Timeout:
                pass
        time.sleep(5)


def start_match(
    podman_url: str,
    image: str,
    match_dir: Path,
    game_root: Path,
    lock_root: Path,
    pin_cpu: dict,
) -> int:
    with PodmanClient(base_url=podman_url) as podman:
        cpu = None
        if pin_cpu["min"] != -1 and pin_cpu["max"] != -1:
            cpu = select_cpu(lock_root)

        try:
            kwargs = {
                "image": image,
                "mounts": [
                    {
                        "type": "bind",
                        "source": str(match_dir.absolute()),
                        "target": "/match",
                        "read_only": False,
                    },
                    {
                        "type": "bind",
                        "source": str((game_root / "server").absolute()),
                        "target": "/server",
                        "read_only": True,
                    },
                    {
                        "type": "bind",
                        "source": str((game_root / "bundle" / "data").absolute()),
                        "target": "/bundle",
                        "read_only": True,
                    },
                    {
                        "type": "bind",
                        "source": str((game_root / "players").absolute()),
                        "target": "/players",
                        "read_only": True,
                    },
                ],
                "network_mode": "none",
                "userns_mode": "keep-id",
            }
            if cpu:
                kwargs["cpuset_cpus"] = str(cpu.cpu)
            container = podman.containers.create(**kwargs)

            try:
                container.start()
                container.wait(condition="exited")
                inspect = container.inspect()
                return inspect["State"]["ExitCode"]
            finally:
                container.remove()
        finally:
            if cpu:
                logger.info(f"Releasing lock for CPU {cpu.cpu}.")
                cpu.lock.release()
