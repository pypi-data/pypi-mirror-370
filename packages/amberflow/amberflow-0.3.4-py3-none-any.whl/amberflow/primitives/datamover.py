from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path

from amberflow.primitives import dirpath_t, _run_command

__all__ = ("DataMover", "RsyncMover")


class DataMover(ABC):
    """Abstract base class for data transfer strategies."""

    @abstractmethod
    def upload(self, local_path: dirpath_t, remote_path: dirpath_t, logger: Logger, **kwargs) -> None:
        """Uploads data from a local path to a remote path."""
        pass

    @abstractmethod
    def download(self, remote_path: dirpath_t, local_path: dirpath_t, logger: Logger, **kwargs) -> None:
        """Downloads data from a remote path to a local path."""
        pass


class RsyncMover(DataMover):
    """Data mover that uses rsync over SSH."""

    def __init__(self, remote_server: str):
        self.remote_server = remote_server

    def upload(self, local_path: dirpath_t, remote_path: dirpath_t, logger: Logger, **kwargs) -> None:
        src = f"{local_path}/"
        dest = f"{self.remote_server}:{remote_path}/"
        self._run_rsync(src, dest, logger, **kwargs)

    def download(self, remote_path: dirpath_t, local_path: dirpath_t, logger: Logger, **kwargs) -> None:
        src = f"{self.remote_server}:{remote_path}/"
        dest = f"{local_path}/"
        self._run_rsync(src, dest, logger, **kwargs)

    @staticmethod
    def _run_rsync(src: str, dest: str, logger: Logger, **kwargs):
        exclude = kwargs.get("exclude")
        cmd_list = ["rsync", "-avzu", "--delete"]
        if exclude:
            for item in exclude:
                cmd_list.append(f"--exclude='{item}'")
        cmd_list.extend([src, dest])

        cmd_str = " ".join(cmd_list)
        logger.debug(f"Running rsync:\n{cmd_str}")
        _run_command(cmd_str, cwd=Path.cwd(), logger=logger, check=True)
