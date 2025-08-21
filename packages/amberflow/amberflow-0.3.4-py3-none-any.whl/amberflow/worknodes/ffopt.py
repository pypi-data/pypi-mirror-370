from pathlib import Path
from typing import Any, Union

from parmed import load_file

# noinspection PyProtectedMember
from parmed.tools.actions import deleteDihedral, addDihedral
from parmed.amber.mask import AmberMask

from amberflow.artifacts import ArtifactContainer, BatchArtifacts, BaseTopologyFile
from amberflow.primitives import dirpath_t, filepath_t
from amberflow.worknodes import BaseSingleWorkNode, worknodehelper

__all__ = ("FFOPT",)


# noinspection DuplicatedCode,PyTypeChecker
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseTopologyFile,),
    output_artifact_types=(BaseTopologyFile,),
)
class FFOPT(BaseSingleWorkNode):
    def __init__(
        self,
        wnid: str,
        *args,
        resname: str = "LIG",
        scee: float = 1.2,
        scnb: float = 2.0,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.resname = resname
        self.scee = scee
        self.scnb = scnb

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        intop = self.input_artifacts["BaseTopologyFile"]
        outparm = self.work_dir / intop.filepath.name
        if self.skippable:
            if self._try_and_skip(sysname, outparm=outparm):
                return self.output_artifacts

        p = load_file(str(intop.filepath))

        # Find atoms within two bonds of atom type 'ne'
        # noinspection PyUnresolvedReferences
        ne_atoms = [
            atom
            for atom in p.atoms
            if ((atom.type.lower() == "ne" or atom.type.lower() == "nf") and atom.residue.name == self.resname)
        ]
        if len(ne_atoms) != 1:
            err_msg = f"Invalid 'ne' atom count found in the residue ({ne_atoms=}). Please ensure there's exactly one 'ne' atom is present."
            self.node_logger.error(err_msg)
            raise Exception(err_msg)
        ne_atom = ne_atoms[0]

        within_two_bonds = set()
        # First neighbors (one bond away)
        first_neighbors = ne_atom.bond_partners
        within_two_bonds.update(first_neighbors)
        # Second neighbors (two bonds away)
        for neighbor in first_neighbors:
            second_neighbors = neighbor.bond_partners
            within_two_bonds.update(second_neighbors)

        # Remove the original 'ne' atoms from the set
        within_two_bonds.difference_update(ne_atoms)

        # Find the carbon atom bonded to both an 'ss' type atom and the 'ne' atom
        carbon_bonded_to_ss_and_ne = None
        for atom in within_two_bonds:
            if atom.type.lower().startswith("c"):
                bonded_types = [partner.type.lower() for partner in atom.bond_partners]
                if "ss" in bonded_types and ("ne" in bonded_types or "nf" in bonded_types):
                    carbon_bonded_to_ss_and_ne = atom
                    break

        if carbon_bonded_to_ss_and_ne is None:
            raise Exception("No carbon atom bonded to both 'ss' and 'ne' found within two bonds of 'ne'.")
        print(
            f"Carbon atom bonded to both 'ss' and 'ne': {carbon_bonded_to_ss_and_ne.name} (index {carbon_bonded_to_ss_and_ne.idx})"
        )

        # Find the other carbon atom bonded to 'ne' but not to 'ss'
        other_carbon_bonded_to_ne = None
        for atom in within_two_bonds:
            if atom.type.lower().startswith("c"):
                bonded_types = [partner.type.lower() for partner in atom.bond_partners]
                if ("ne" in bonded_types or "nf" in bonded_types) and "ss" not in bonded_types:
                    other_carbon_bonded_to_ne = atom
                    break

        if other_carbon_bonded_to_ne is None:
            raise Exception("No carbon atom bonded to 'ne' and not to 'ss' found within two bonds of 'ne'.")
        print(
            f"Other carbon atom bonded to 'ne' and not to 'ss': {other_carbon_bonded_to_ne.name} (index {other_carbon_bonded_to_ne.idx})"
        )

        # Find the oxygen atom bonded to other_carbon_bonded_to_ne
        oxygen_bonded_to_other_carbon = None
        for partner in other_carbon_bonded_to_ne.bond_partners:
            if partner.type.lower().startswith("o"):
                oxygen_bonded_to_other_carbon = partner
                break

        if oxygen_bonded_to_other_carbon is None:
            raise Exception(f"No oxygen atom bonded to {other_carbon_bonded_to_ne.name} found.")
        print(
            f"Oxygen atom bonded to {other_carbon_bonded_to_ne.name}: {oxygen_bonded_to_other_carbon.name} (index {oxygen_bonded_to_other_carbon.idx})"
        )

        # Find the 'ss' atom bonded to carbon_bonded_to_ss_and_ne
        ss_atom = None
        for partner in carbon_bonded_to_ss_and_ne.bond_partners:
            if partner.type.lower() == "ss":
                ss_atom = partner
                break

        if ss_atom is None:
            raise Exception(f"No 'ss' atom bonded to {carbon_bonded_to_ss_and_ne.name} found.")
        print(f"'ss' atom bonded to {carbon_bonded_to_ss_and_ne.name}: {ss_atom.name} (index {ss_atom.idx})")

        # Find the nitrogen atom bonded to carbon_bonded_to_ss_and_ne
        nitrogen_bonded_to_carbon = None
        for partner in carbon_bonded_to_ss_and_ne.bond_partners:
            if partner.type.lower().startswith("n") and partner != ne_atom:
                nitrogen_bonded_to_carbon = partner
                break

        if nitrogen_bonded_to_carbon is None:
            raise Exception(f"No nitrogen atom bonded to {carbon_bonded_to_ss_and_ne.name} found.")
        print(
            f"Nitrogen atom bonded to {carbon_bonded_to_ss_and_ne.name}: {nitrogen_bonded_to_carbon.name} (index {nitrogen_bonded_to_carbon.idx})"
        )

        # Find the carbon atom bonded to the carbon bonded to other_carbon_bonded_to_ne
        carbon_bonded_to_other_carbon = None
        for partner in other_carbon_bonded_to_ne.bond_partners:
            if partner.type.lower().startswith("c") and partner != oxygen_bonded_to_other_carbon:
                carbon_bonded_to_other_carbon = partner
                break

        if carbon_bonded_to_other_carbon is None:
            raise Exception(f"No carbon atom bonded to {other_carbon_bonded_to_ne.name} (excluding oxygen) found.")
        print(
            f"Carbon atom bonded to {other_carbon_bonded_to_ne.name}: {carbon_bonded_to_other_carbon.name} (index {carbon_bonded_to_other_carbon.idx})"
        )

        # Find the two other carbon atoms bonded to carbon_bonded_to_other_carbon
        other_carbons_bonded = []
        for partner in carbon_bonded_to_other_carbon.bond_partners:
            if partner.type.lower().startswith("c") and partner != other_carbon_bonded_to_ne:
                other_carbons_bonded.append(partner)

        if len(other_carbons_bonded) != 2:
            raise Exception(
                f"Expected 2 other carbons bonded to {carbon_bonded_to_other_carbon.name}, found {len(other_carbons_bonded)}."
            )

        print(
            f"Other carbons bonded to {carbon_bonded_to_other_carbon.name}: {[atom.name for atom in other_carbons_bonded]} (indices {[atom.idx for atom in other_carbons_bonded]})"
        )

        mask = f":{self.resname}@{other_carbons_bonded[0].name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{carbon_bonded_to_other_carbon.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{other_carbons_bonded[1].name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{other_carbon_bonded_to_ne.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{oxygen_bonded_to_other_carbon.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{ne_atom.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{ss_atom.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")
        mask = f":{self.resname}@{nitrogen_bonded_to_carbon.name}"
        res = [i for i in AmberMask(p, mask).Selected()]
        if len(res) == 0:
            raise Exception(f"No atoms matching {mask}")

        deleteDihedral(
            p,
            f":{self.resname}@{ss_atom.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ss_atom.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            -0.6104380159930654,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ss_atom.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            -2.484919749058815,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ss_atom.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            -0.6869450510866189,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{nitrogen_bonded_to_carbon.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{nitrogen_bonded_to_carbon.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            1.2690037710703148,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{nitrogen_bonded_to_carbon.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            -1.7967395818879786,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{nitrogen_bonded_to_carbon.name}",
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            0.32936112937894635,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            0.7787614874785769,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            -5.107378515958192,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            -0.056037412113724545,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            1.9024956376089779,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            -3.3346544708199044,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{carbon_bonded_to_ss_and_ne.name}",
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            -0.9950435977166064,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
            0.32935505210203775,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
            -0.31149635696913586,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
            -0.07052305978537719,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
            0.32935505210203775,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
            -0.31149635696913586,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{oxygen_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
            -0.07052305978537719,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
            0.4182428395538059,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
            -0.2964983828847052,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[0].name}",
            0.02918144015727811,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        deleteDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
            0.4182428395538059,
            1,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
            -0.2964983828847052,
            2,
            0,
            self.scee,
            self.scnb,
        ).execute()
        addDihedral(
            p,
            f":{self.resname}@{ne_atom.name}",
            f":{self.resname}@{other_carbon_bonded_to_ne.name}",
            f":{self.resname}@{carbon_bonded_to_other_carbon.name}",
            f":{self.resname}@{other_carbons_bonded[1].name}",
            0.02918144015727811,
            3,
            0,
            self.scee,
            self.scnb,
        ).execute()

        # noinspection PyUnresolvedReferences
        p.save(str(outparm), overwrite=True)
        self.output_artifacts = self.fill_output_artifacts(sysname, outparm=outparm)
        return self.output_artifacts

    def _try_and_skip(self, sysname: str, *, outparm: Path) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, outparm=outparm)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
            except ValueError as e:
                self.node_logger.info(f"Can't skip {self.id}. Got {e}")
        return False

    def fill_output_artifacts(self, sysname: str, *, outparm: filepath_t) -> Union[ArtifactContainer, BatchArtifacts]:
        return ArtifactContainer(sysname, (self.artifact_builder["BaseTopologyFile"](outparm),))
