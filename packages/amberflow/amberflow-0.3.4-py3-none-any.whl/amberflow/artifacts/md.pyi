from typing import List, Type, Any
from amberflow.primitives import filepath_t
from amberflow.artifacts import BaseArtifactFile

__all__ = (
    "BoreschRestraints",
    "CpptrajData",
    "Groupfile",
    "LambdaScheduleFile",
    "Remlog",
    "BaseMdoutMD",
    "TargetProteinMdoutMD",
    "TargetNucleicMdoutMD",
    "BinderLigandMdoutMD",
    "ComplexProteinLigandMdoutMD",
    "ComplexNucleicLigandMdoutMD",
)

class BoreschRestraints(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(
        self,
        filepath: filepath_t,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...

class CpptrajData(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...

class Groupfile(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...
    @classmethod
    def from_lines(cls: Type["Groupfile"], filepath: filepath_t, lines: List[str]) -> "Groupfile": ...

class LambdaScheduleFile(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...

class Remlog(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None: ...

class BaseMdoutMD(BaseArtifactFile):
    def __init__(self, filepath: filepath_t, *args: Any, check: bool = True, **kwargs: Any) -> None: ...
    @staticmethod
    def check_mdout(mdout: filepath_t) -> None: ...

class TargetProteinMdoutMD(BaseMdoutMD):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, check: bool = True, **kwargs: Any) -> None: ...

class TargetNucleicMdoutMD(BaseMdoutMD):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, check: bool = True, **kwargs: Any) -> None: ...

class BinderLigandMdoutMD(BaseMdoutMD):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, check: bool = True, **kwargs: Any) -> None: ...

class ComplexProteinLigandMdoutMD(BaseMdoutMD):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, check: bool = True, **kwargs: Any) -> None: ...

class ComplexNucleicLigandMdoutMD(BaseMdoutMD):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, check: bool = True, **kwargs: Any) -> None: ...
