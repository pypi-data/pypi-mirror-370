import pickle
from pathlib import Path
from typing import Union

import networkx as nx
from attrs import field, frozen

from amberflow.primitives import FileHandle


__all__ = [
    "CheckPoint",
]


@frozen
class CheckPoint:
    file: FileHandle = field(converter=lambda value: FileHandle(value))
    project_dag: nx.DiGraph = field(default=nx.DiGraph(), kw_only=True)
    compute_dag: nx.DiGraph = field(default=nx.DiGraph(), kw_only=True)

    def __attrs_post_init__(self) -> None:
        pass

    @classmethod
    def from_existing(cls, file: Union[Path, FileHandle]) -> "CheckPoint":
        with open(file, "rb") as cur_file:
            tracking = pickle.load(cur_file)
        return cls(file, project_dag=tracking["project_dag"], compute_dag=tracking["compute_dag"])

    @classmethod
    def from_empty(cls, file: Path) -> "CheckPoint":
        file.touch()
        return cls(file=file)  # type: ignore

    def track(self) -> None:
        tracking = {
            "project_dag": self.project_dag,
            "compute_dag": self.compute_dag,
        }
        with open(self.file, "wb") as cur_file:
            pickle.dump(tracking, cur_file)
