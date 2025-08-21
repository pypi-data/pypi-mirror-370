from pathlib import Path
from typing import Optional, Sequence, Union, SupportsIndex, Iterator

import numpy as np

from amberflow.artifacts import fileartifact, BaseArtifact, BaseArtifactFile, BaseArtifactDir, BaseMdoutMD
from amberflow.primitives import filepath_t, FileHandle

__all__ = (
    "LambdaSchedule",
    "BaseStatesFile",
    "BaseRestartStatesFile",
    "BaseTrajectoryStatesFile",
    "ComplexProteinLigandRestartStates",
    "BinderLigandRestartStates",
    "ComplexNucleicLigandRestartStates",
    "ComplexProteinLigandTrajectoryStatesNC",
    "BinderLigandTrajectoryStatesNC",
    "ComplexNucleicLigandTrajectoryStates",
    "MdoutStates",
    "EdgeMBARhtml",
    "EdgeMBARxml",
    "Datdir",
    "TargetDatdir",
    "ReferenceDatdir",
)


class LambdaSchedule(BaseArtifact):
    """
    A class representing a schedule of lambda values for alchemical transformations.

    Lambda values are used in alchemical free energy calculations to define the
    intermediate states between two end states.
    """

    tags: tuple = ("",)

    def __init__(self, lambdas: Sequence[float], decimals: int = 5) -> None:
        """
        Initialize a LambdaSchedule with a sequence of lambda values.

        Parameters
        ----------
        lambdas : Sequence[float]
            A sequence of lambda values between 0 and 1
        decimals : int, optional
            Number of decimal places to round lambda values to, by default 5
        """
        self.lambdas = np.array(lambdas)
        # Just setting a default large number
        self.decimals = 20
        if decimals != 0:
            self.lambdas = np.round(self.lambdas, decimals=5)
            self.decimals = decimals

    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[float, "LambdaSchedule"]:
        if isinstance(index, slice):
            return type(self)(self.lambdas[index])
        return float(self.lambdas[index])

    def __iter__(self) -> Iterator[float]:
        for x in self.lambdas:
            yield float(x)

    def get_formatted(self, index: Union[SupportsIndex]) -> str:
        return f"{self[index]:.{self.decimals}f}"

    def formatted(self) -> Iterator[str]:
        for x in self.lambdas:
            yield f"{x:.{self.decimals}f}"

    def __contains__(self, item: float) -> bool:
        return item in self.lambdas

    def __repr__(self) -> str:
        return f"{type(self).__name__}(lambdas={self.lambdas.tolist()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented(f"Bad comparison between {type(self)} and {type(other)}")
        return np.array_equal(self.lambdas, other.lambdas)

    def __len__(self) -> int:
        return len(self.lambdas)


class BaseStatesFile(BaseArtifact):
    """
    Base class for managing collections of state files in alchemical simulations.

    This class provides functionality to handle multiple files corresponding to different
    lambda states in an alchemical transformation.
    """

    def __init__(
        self, filepath: filepath_t, *args, prefix, suffix, lambdas: Optional[Sequence[float]] = None, **kwargs
    ) -> None:
        """
        Initialize a BaseStatesFile object.

        Parameters
        ----------
        filepath : filepath_t
            Path to a representative file in the collection
        prefix : str
            Prefix for the filenames
        suffix : str
            Suffix (extension) for the filenames
        lambdas : Optional[Sequence[float]], optional
            Sequence of lambda values, by default None
        """
        self.filepath = Path(FileHandle(filepath))
        self.name: str = self.filepath.stem[len(prefix) + 1 :]
        super()._check_file(self.filepath, prefix, suffix)
        # use FileHandle to ensure the files exist
        if lambdas is not None:
            name_wo_clambda = "_".join(filepath.stem.split("_")[:-1])
            self.states = {
                float(clambda): FileHandle(filepath.with_name(f"{name_wo_clambda}_{clambda}{suffix}"))
                for clambda in lambdas
            }
        else:
            prefix = prefix if prefix != "" else "*"
            self.states = {}
            for state in sorted(filepath.parent.glob(f"{prefix}_*{suffix}")):
                try:
                    clambda = float(state.stem.split("_")[-1])
                except ValueError:
                    # If the last part of the filename is not a float, skip this file
                    continue
                if 0 <= clambda <= 1:
                    self.states[clambda] = state

        self.nlambdas = len(self.states)

    def __getitem__(self, key: float) -> filepath_t:
        return self.states[key]

    def __iter__(self) -> Iterator[FileHandle]:
        return iter(self.states.values())

    def __len__(self) -> int:
        return len(self.states)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(states={self.states})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(states={self.states})"

    def values(self):
        return self.states.values()

    def keys(self):
        return self.states.keys()

    def items(self):
        return self.states.items()

    def get(self, key, default=None):
        return self.states.get(key, default)

    @staticmethod
    def get_name(filepath: Path, prefix: str) -> str:
        return filepath.stem[len(prefix) :]

    def __fspath__(self) -> Union[str, bytes, Path]:
        return str(self.filepath)


class BaseRestartStatesFile(BaseStatesFile):
    pass


class BaseTrajectoryStatesFile(BaseStatesFile):
    pass


@fileartifact
class ComplexProteinLigandRestartStates(BaseRestartStatesFile):
    prefix: str = "complex"
    suffix: str = ".rst7"
    tags: tuple = ("protein", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class BinderLigandRestartStates(BaseRestartStatesFile):
    prefix: str = "binder"
    suffix: str = ".rst7"
    tags: tuple = ("ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class ComplexNucleicLigandRestartStates(BaseRestartStatesFile):
    prefix: str = "complex"
    suffix: str = ".rst7"
    tags: tuple = ("nucleic", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class ComplexProteinLigandTrajectoryStatesNC(BaseTrajectoryStatesFile):
    prefix: str = "complex"
    suffix: str = ".nc"
    tags: tuple = ("protein", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class BinderLigandTrajectoryStatesNC(BaseTrajectoryStatesFile):
    prefix: str = "binder"
    suffix: str = ".nc"
    tags: tuple = ("ligand", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class ComplexNucleicLigandTrajectoryStates(BaseTrajectoryStatesFile):
    prefix: str = "complex"
    suffix: str = ".nc"
    tags: tuple = ("nucleic", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class MdoutStates(BaseStatesFile):
    prefix: str = ""
    suffix: str = ".mdout"
    tags: tuple[str] = ("alchemical",)

    def __init__(self, filepath: filepath_t, *args, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)
        if check:
            self.check_mdouts(self.states)

    @staticmethod
    def check_mdouts(states: dict[float, FileHandle]) -> None:
        for mdout in states.values():
            BaseMdoutMD.check_mdout(mdout)


@fileartifact
class EdgeMBARhtml(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".html"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class EdgeMBARxml(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".xml"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class Datdir(BaseArtifactDir):
    prefix: str = ""
    suffix: str = ""
    tags: tuple[str] = ("",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        edge: str = "sysname",
        environment: str = "com",
        stage: str = "vdw",
        trial: int = 1,
        states: Optional[Sequence[float]] = None,
        makedir=False,
        **kwargs,
    ) -> None:
        self.edge = edge
        self.environment = environment
        self.stage = stage
        self.trial = f"t{trial}"
        self.states = tuple(states) if states is not None else None
        self.parent_filepath = Path(filepath)
        new_filepath = Path(filepath, self.edge, self.environment, self.stage, self.trial)
        if makedir:
            new_filepath.mkdir(parents=True, exist_ok=True)
        super().__init__(new_filepath, *args, prefix=kwargs.get("prefix"), suffix=kwargs.get("suffix"))

    def is_valid(self, nlambdas: Optional[int] = None, remlog: bool = True, mbar: bool = False) -> bool:
        """
        Check if the directory contains the expected number of lambda states and required files.

        Parameters
        ----------
        nlambdas : int
            Number of lambda states expected.
        remlog : bool, optional
            Whether to require at least one .yaml file (default: True).
        mbar : bool, optional
            Whether to use MBAR file counting logic (default: False). Set it to True only if you're sure your
            run had valid MBAR Energy values for all windows against all windows.

        Returns
        -------
        bool
            True if the directory is valid, False otherwise.
        """
        if nlambdas is None:
            if not (states := getattr(self, "states", False)):
                raise ValueError("The `states` attribute must be set before calling is_valid() without `nlambdas`.")
            nlambdas = len(states)
        # First, check that the directory actually exists
        if not self.filepath.is_dir():
            return False
        if remlog:
            try:
                next(iter(self.filepath.glob("*.yaml")))
            except StopIteration:
                return False
        # Check if the directory contains the expected number of dat files, given the number of lambdas.
        dvdl_count = len(list(self.filepath.glob("dvdl*.dat")))
        if dvdl_count < nlambdas:
            return False
        # if BAR: 3 dat files for each window, except the first and last windows which have 2 dat files each.
        efep_count = len(list(self.filepath.glob("efep*.dat")))
        efep_expected = nlambdas * nlambdas if mbar else (nlambdas - 2) * 3 + 4
        return efep_count >= efep_expected

    def get_path_template(self) -> str:
        if self.stage == "":
            return str(self.parent_filepath / r"{edge}/{env}/{trial}/efep_{traj}_{ene}.dat")
        else:
            return str(self.parent_filepath / r"{edge}/{env}/{stage}/{trial}/efep_{traj}_{ene}.dat")


@fileartifact
class TargetDatdir(Datdir):
    prefix: str = ""
    suffix: str = ""
    tags: tuple[str] = ("target",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        edge: str = "sysname",
        environment: str = "aq",
        stage: str = "vdw",
        trial: int = 1,
        states: Optional[Sequence[float]] = None,
        makedir=False,
        **kwargs,
    ) -> None:
        super().__init__(
            filepath,
            *args,
            edge=edge,
            environment=environment,
            stage=stage,
            trial=trial,
            states=states,
            makedir=makedir,
            prefix=self.prefix,
            suffix=self.suffix,
            **kwargs,
        )
        try:
            self.boresch_restraints = next(iter(getattr(self, "filepath").glob("boresch*.yaml")))
        except StopIteration:
            self.boresch_restraints = None


@fileartifact
class ReferenceDatdir(Datdir):
    prefix: str = ""
    suffix: str = ""
    tags: tuple[str] = ("reference",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        edge: str = "sysname",
        environment: str = "com",
        stage: str = "vdw",
        trial: int = 1,
        states: Optional[Sequence[float]] = None,
        makedir=False,
        **kwargs,
    ) -> None:
        super().__init__(
            filepath,
            *args,
            edge=edge,
            environment=environment,
            stage=stage,
            trial=trial,
            states=states,
            makedir=makedir,
            prefix=self.prefix,
            suffix=self.suffix,
            **kwargs,
        )
