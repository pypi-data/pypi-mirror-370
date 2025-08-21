from amberflow.artifacts import fileartifact, BaseArtifactFile
from amberflow.primitives import filepath_t, find_word_and_get_line, BadMDout

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


@fileartifact
class BoreschRestraints(BaseArtifactFile):
    prefix: str = "rest"
    suffix: str = ".in"
    tags: tuple = ("alchemical",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class CpptrajData(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".dat"
    tags: tuple[str] = ("cpptraj",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class Groupfile(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".groupfile"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)

    @classmethod
    def from_lines(cls, filepath: filepath_t, lines: list[str]) -> "Groupfile":
        """Create a Groupfile from a list of lines."""
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
            f.write("\n")
        return cls(filepath)


@fileartifact
class LambdaScheduleFile(BaseArtifactFile):
    prefix: str = "lambda"
    suffix: str = ".sch"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class Remlog(BaseArtifactFile):
    prefix: str = "remd"
    suffix: str = ".log"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


class BaseMdoutMD(BaseArtifactFile):
    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, **kwargs)
        if check:
            BaseMdoutMD.check_mdout(filepath)

    @staticmethod
    def check_mdout(mdout: filepath_t) -> None:
        if not find_word_and_get_line(mdout, "Total wall time:"):
            raise BadMDout(f"Cannot find 'Total wall time' in {mdout}\nMDout file may be incomplete or corrupted.")


@fileartifact
class TargetProteinMdoutMD(BaseMdoutMD):
    prefix: str = "target"
    suffix: str = ".mdout"
    tags: tuple[str] = ("target", "protein")

    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, check=check, **kwargs)


@fileartifact
class TargetNucleicMdoutMD(BaseMdoutMD):
    prefix: str = "target"
    suffix: str = ".mdout"
    tags: tuple[str] = ("target", "nucleic")

    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, check=check, **kwargs)


@fileartifact
class BinderLigandMdoutMD(BaseMdoutMD):
    prefix: str = "binder"
    suffix: str = ".mdout"
    tags: tuple[str] = ("ligand",)

    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, check=check, **kwargs)


@fileartifact
class ComplexProteinLigandMdoutMD(BaseMdoutMD):
    prefix: str = "complex"
    suffix: str = ".mdout"
    tags: tuple[str] = ("protein", "ligand")

    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, check=check, **kwargs)


@fileartifact
class ComplexNucleicLigandMdoutMD(BaseMdoutMD):
    prefix: str = "complex"
    suffix: str = ".mdout"
    tags: tuple[str] = ("nucleic", "ligand")

    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, check=check, **kwargs)
