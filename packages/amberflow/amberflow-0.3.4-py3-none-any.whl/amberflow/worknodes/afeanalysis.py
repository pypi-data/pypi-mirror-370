import shutil
import xml.etree.ElementTree as ElementTree
from itertools import chain
from pathlib import Path
from typing import Any, Optional, Final

import numpy as np
import yaml
from edgembar.amber2dats import extract_traditional_ti, remd_analysis, read_rst_file, read_rem_log

from amberflow.artifacts import (
    MdoutStates,
    BoreschRestraints,
    Remlog,
    EdgeMBARxml,
    Datdir,
    TargetDatdir,
    ReferenceDatdir,
    ArtifactContainer,
    EdgeMBARhtml,
)
from amberflow.primitives import filepath_t, dirpath_t, capture_stdout
from amberflow.worknodes import BaseAnalysis, worknodehelper

__all__ = (
    "Amber2Dats",
    "GetXML",
    "EdgeMBAR",
)


@worknodehelper(
    file_exists=True,
    input_artifact_types=(
        MdoutStates,
        Remlog,
    ),
    optional_artifact_types=(BoreschRestraints,),
    output_artifact_types=(Datdir,),
)
class Amber2Dats(BaseAnalysis):
    def __init__(
        self,
        wnid: str,
        *args,
        mdin_template: str = "md",
        edge: str = "sysname",
        environment: str = "com",
        stage: str = "vdw",
        trial: int = 1,
        target: bool = True,
        nan: Optional[float] = None,
        exclude_untrustworthy_samples: bool = False,
        nmax: int = 10000,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            mdin_template=mdin_template,
            **kwargs,
        )
        self.edge = edge
        self.environment = environment
        self.stage = stage
        self.trial = trial
        self.datdir_type = TargetDatdir if target else ReferenceDatdir

        self.nan = nan
        self.exclude_untrustworthy_samples = exclude_untrustworthy_samples
        self.nmax = nmax

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        # Get the output directory structure
        edge = sysname if self.edge == "sysname" else self.edge
        mdouts = self.input_artifacts["MdoutStates"]
        trial_dir = self.datdir_type(
            self.work_dir,
            edge=edge,
            environment=self.environment,
            stage=self.stage,
            trial=self.trial,
            states=mdouts.states.keys(),
            makedir=True,
        )
        if self._try_and_skip(sysname=sysname, trial_dir=trial_dir):
            return self.output_artifacts

        # Restraints
        boresch_file = (
            Path(self.input_artifacts["BoreschRestraints"]) if "BoreschRestraints" in self.input_artifacts else None
        )
        if boresch_file:
            with capture_stdout():
                read_rst_file(boresch_file, Path(trial_dir))

        # remlog
        with capture_stdout():
            reptraj, nstate, nexch, nsucc, acceptance_ratios = read_rem_log(Path(self.input_artifacts["Remlog"]))
            remd_analysis(reptraj, acceptance_ratios, Path(trial_dir))

        # mdouts
        with capture_stdout():
            for mdout in mdouts:
                extract_traditional_ti(
                    mdout,
                    write=True,
                    odir=Path(trial_dir),
                    skip_bad=self.exclude_untrustworthy_samples,
                    maxsamples=self.nmax,
                    undefene=self.nan,
                )

        self.output_artifacts = self.fill_output_artifacts(sysname=sysname, trial_dir=trial_dir)

        return self.output_artifacts

    # noinspection DuplicatedCode
    def _try_and_skip(self, sysname: str, *, trial_dir: Datdir) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname=sysname, trial_dir=trial_dir)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
            except ValueError as e:
                self.node_logger.info(f"Can't skip {self.id}. Got {e}")
        return False

    def fill_output_artifacts(
        self,
        sysname: str,
        *,
        trial_dir: Datdir,
    ) -> ArtifactContainer:
        if trial_dir.is_valid():
            return ArtifactContainer(sysname, (trial_dir,))
        else:
            raise FileNotFoundError(f"{self.__class__.__name__}: The trial directory {trial_dir} is invalid.")


@worknodehelper(
    file_exists=True,
    input_artifact_types=(Datdir,),
    output_artifact_types=(EdgeMBARxml,),
)
class GetXML(BaseAnalysis):
    map_to_edgembar: dict[str, str] = {
        "com": "target",
        "aq": "reference",
    }

    def __init__(
        self,
        wnid: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        xml_path = Path(self.work_dir, f"edge_{sysname}.xml")
        if self._try_and_skip(sysname=sysname, edges_xml=xml_path):
            return self.output_artifacts

        # Assume the edge name is the same for all results and take it from the first one.
        edge_name = next(iter(self.input_artifacts.values()))[0].edge
        root = ElementTree.Element("edge", name=edge_name)
        edges = set()
        for dir_list in self.input_artifacts.values():
            for datdir in dir_list:
                edges.add(datdir.edge)
                self.add_trial(root, datdir)
        if len(edges) > 1:
            raise ValueError(f"Multiple edges found: {edges}. Expected only one edge per run.")

        # Create the full XML tree and write it to the file
        tree = ElementTree.ElementTree(root)
        # 'indent' makes the XML human-readable
        ElementTree.indent(tree, space="\t", level=0)

        tree.write(str(xml_path), xml_declaration=True, encoding="utf-8", method="xml")

        self.output_artifacts = self.fill_output_artifacts(sysname=sysname, edges_xml=xml_path)

        return self.output_artifacts

    def add_trial(self, root: ElementTree.Element, datdir: Datdir) -> None:
        # Use dictionaries to keep track of created elements to avoid duplicates
        env_elements: dict[str, ElementTree.Element] = {}
        # Get or create the <env> element
        env_name = datdir.environment
        if env_name not in env_elements:
            env_element = ElementTree.SubElement(root, "env", name=self.map_to_edgembar[env_name])
            env_elements[env_name] = env_element
        else:
            env_element = env_elements[env_name]
        #
        stage_element = ElementTree.SubElement(env_element, "stage", name=datdir.stage)
        trial_element = ElementTree.SubElement(stage_element, "trial", name=datdir.trial)

        # Add the <dir> element
        dir_element = ElementTree.SubElement(trial_element, "dir")
        dir_element.text = str(datdir.filepath)

        # Add the optional <shift> element
        if boresch_fn := getattr(datdir, "boresch_restraints", None):
            shift_element = ElementTree.SubElement(trial_element, "shift")
            shift = self.parse_offset_from_boresch(boresch_fn)
            shift_element.text = f"{shift:.5f}"

        # Add all the <ene> elements
        for window in datdir.states:
            ene_element = ElementTree.SubElement(trial_element, "ene")
            ene_element.text = f"{window:.8f}"

    # noinspection DuplicatedCode
    def _try_and_skip(self, sysname: str, *, edges_xml: Path) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname=sysname, edges_xml=edges_xml)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
            except ValueError as e:
                self.node_logger.info(f"Can't skip {self.id}. Got {e}")
        return False

    # noinspection PyPep8Naming
    @staticmethod
    def parse_offset_from_boresch(boresch_fn: filepath_t) -> float:
        kb: Final[float] = 0.0019872  # kcal/(mol*K)
        T: Final[float] = 298.0  # K
        V0: Final[float] = 1660.0  # Angstroms^3 - Standard State volume for 1M

        k_rst = []
        eq0_rst = []
        with open(boresch_fn, "r") as fh:
            # noinspection PyUnresolvedReferences
            data = yaml.safe_load(fh)
            if "Angle" in data:
                angle_data = data["Angle"]
                # Flatten r2 and process every number
                if "r2" in angle_data:
                    r2_flat = list(chain.from_iterable(angle_data["r2"]))
                    for val in r2_flat:
                        num = float(val)
                        eq0_rst.append(np.sin(num * np.pi / 180.0))
                # Flatten rk2 and process every number
                if "rk2" in angle_data:
                    rk2_flat = list(chain.from_iterable(angle_data["rk2"]))
                    for val in rk2_flat:
                        num = float(val)
                        k_rst.append(num)
            if "Bond" in data:
                bond_data = data["Bond"]
                if "r2" in bond_data:
                    r2_flat = list(chain.from_iterable(bond_data["r2"]))
                    for val in r2_flat:
                        num = float(val)
                        eq0_rst.append(num**2)
                if "rk2" in bond_data:
                    rk2_flat = list(chain.from_iterable(bond_data["rk2"]))
                    for val in rk2_flat:
                        num = float(val)
                        k_rst.append(num)
            if dihedral_data := data["Dihedral"]:
                # For Dihedral, only rk2 is used (Jacobian doesn't take theta angle into account. The volume is the same across all theta angles)
                if "rk2" in dihedral_data:
                    rk2_flat = list(chain.from_iterable(dihedral_data["rk2"]))
                    for val in rk2_flat:
                        num = float(val)
                        k_rst.append(num)
            if len(k_rst) == 0:
                raise RuntimeError(f"Could not parse Boresch restraints from: {boresch_fn}")
            kk = np.prod(k_rst)
            rr = np.prod(eq0_rst)

            # noinspection PyTypeChecker
            dAr = -kb * T * np.log(((8 * np.pi**2 * V0) / rr) * ((kk**0.5) / ((np.pi * kb * T) ** 3)))
        return dAr

    @staticmethod
    def fill_output_artifacts(
        sysname: str,
        *,
        edges_xml: Path,
    ) -> ArtifactContainer:
        return ArtifactContainer(sysname, (EdgeMBARxml(edges_xml),))


@worknodehelper(
    file_exists=True,
    input_artifact_types=(EdgeMBARxml,),
    output_artifact_types=(EdgeMBARhtml,),
)
class EdgeMBAR(BaseAnalysis):
    min_cores: int = 1

    def __init__(
        self,
        wnid: str,
        *args,
        threads: int = 1,
        temp: float = 298.0,
        tol: float = 1e-13,
        btol: float = 1e-07,
        ptol: float = 0.05,
        nboot: int = 20,
        verbosity: int = 0,
        ncon: float = 2,
        dcon: float = 2.0,
        ntimes: int = 4,
        fstart: float = 0.0,
        fstop: float = 1.0,
        fmaxeq: float = 0.5,
        ferreq: float = -1.0,
        stride: int = 1,
        halves: bool = True,
        fwdrev: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.min_cores = threads
        self.binary = "edgembar" if threads == 1 else f"OMP_NUM_THREADS={threads} edgembar_omp"
        self.temp = temp
        self.tol = tol
        self.btol = btol
        self.ptol = ptol
        self.nboot = nboot
        self.verbosity = verbosity
        self.ncon = ncon
        self.dcon = dcon
        self.ntimes = ntimes
        self.fstart = fstart
        self.fstop = fstop
        self.fmaxeq = fmaxeq
        self.ferreq = ferreq
        self.stride = stride
        self.halves = halves
        self.fwdrev = fwdrev

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        in_xml = Path(self.input_artifacts["EdgeMBARxml"])
        out_html = Path(self.work_dir, in_xml.stem + ".html")
        if self._try_and_skip(sysname=sysname, out_html=out_html):
            return self.output_artifacts

        here_xml = self.work_dir / in_xml.name
        shutil.copy(in_xml, here_xml)

        out_py = self.work_dir / in_xml.with_suffix(".py").name

        # use relative paths for the command line
        cmd_line = [
            self.binary,
            f"--temp {self.temp}",
            f"--tol {self.tol}",
            f"--btol {self.btol}",
            f"--ptol {self.ptol}",
            f"--nboot {self.nboot}",
            f"--verbosity {self.verbosity}",
            f"--ncon {self.ncon}",
            f"--dcon {self.dcon}",
            f"--ntimes {self.ntimes}",
            f"--fstart {self.fstart}",
            f"--fstop {self.fstop}",
            f"--fmaxeq {self.fmaxeq}",
            f"--ferreq {self.ferreq}",
            f"--stride {self.stride}",
            f"{in_xml.name}",
        ]
        if self.halves:
            cmd_line.append("--halves")
        if self.fwdrev:
            cmd_line.append("--fwdrev")
        self.command.run(
            cmd_line,
            cwd=self.work_dir,
            logger=self.node_logger,
            expected=(out_py,),
        )

        out_html = out_py.with_suffix(".html")
        self.command.run(
            ["python", str(out_py)],
            cwd=self.work_dir,
            logger=self.node_logger,
            expected=(out_html,),
        )

        self.output_artifacts = self.fill_output_artifacts(sysname=sysname, out_html=out_html)
        return self.output_artifacts

    # noinspection DuplicatedCode
    def _try_and_skip(self, sysname: str, *, out_html: Path) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname=sysname, out_html=out_html)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
            except ValueError as e:
                self.node_logger.info(f"Can't skip {self.id}. Got {e}")
        return False

    @staticmethod
    def fill_output_artifacts(
        sysname: str,
        *,
        out_html: Path,
    ) -> ArtifactContainer:
        return ArtifactContainer(sysname, (EdgeMBARhtml(out_html),))
