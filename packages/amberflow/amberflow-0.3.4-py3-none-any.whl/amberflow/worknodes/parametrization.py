from pathlib import Path

from ligandparam.recipes import LazierLigand

from amberflow.artifacts import ArtifactContainer
from amberflow.artifacts.structure import BinderLigandPDB, BinderLigandMol2
from amberflow.artifacts.topology import LigandLib, LigandFrcmod, Charge
from amberflow.primitives import dirpath_t
from amberflow.worknodes import worknodehelper, AntechamberMixin
from amberflow.worknodes.baseworknode import BaseSingleWorkNode

__all__ = [
    "ParametrizeBinderBCC",
]


@worknodehelper(file_exists=True, input_artifact_types=(BinderLigandPDB,), optional_artifact_types=(Charge,))
class ParametrizeBinderBCC(BaseSingleWorkNode, AntechamberMixin):
    """Parametrize a ligand using the AmberTools antechamber and tleap programs.

    TODO: Add an artifact for the charge. Right now this applies all the same net charges."""

    def __init__(
        self,
        wnid: str,
        *args,
        resname: str = "LIG",
        atom_type: str = "gaff2",
        charge_model: str = "abcg2",
        charge: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.resname = resname
        super().check_supported(atom_type, "atom_type")
        self.atom_type = atom_type
        super().check_supported(charge_model, "charge_model")
        self.charge_model = charge_model
        self.charge = charge

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        if self._try_and_skip(sysname):
            return self.output_artifacts

        recipe = LazierLigand(
            in_filename=Path(self.input_artifacts["BinderLigandPDB"]),
            cwd=self.work_dir,
            atom_type=self.atom_type,
            charge_model=self.charge_model,
            logger=self.node_logger,
            molname=self.resname,
            net_charge=int(self.input_artifacts.get("Charge", self.charge)),
        )
        recipe.setup()
        recipe.execute()
        self.output_artifacts = self.fill_output_artifacts(sysname, output_dir=self.work_dir)
        return self.output_artifacts

    def _try_and_skip(self, sysname: str) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, output_dir=self.work_dir)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
        return False

    @staticmethod
    def fill_output_artifacts(sysname: str, *, output_dir: dirpath_t) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            [
                BinderLigandPDB(output_dir / f"binder_{sysname}.pdb"),
                BinderLigandMol2(output_dir / f"binder_{sysname}.mol2"),
                LigandLib(output_dir / f"binder_{sysname}.lib"),
                LigandFrcmod(output_dir / f"binder_{sysname}.frcmod"),
            ],
        )
