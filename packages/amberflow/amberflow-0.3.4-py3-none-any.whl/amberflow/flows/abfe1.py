from typing import Optional

import attrs

from amberflow.flows import BaseFlow
from amberflow.worknodes import (
    QuickLambdaSchedule,
    LambdaAnhilation,
    CreateReferenceStructure,
    LambdaMDRun,
    Amber2Dats,
    GetXML,
    EdgeMBAR,
    WorkNodeFilter,
)
from amberflow.artifacts import (
    AnhilateParameters,
    LambdaParameters,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    BaseBinderStructureFile,
    BaseComplexStructureFile,
    BoreschRestraints,
)

__all__ = ("FlowABFE1",)


class FlowABFE1(BaseFlow):
    """
    This flow runs the alchemical free energy calculations for both the complex
    and ligand systems. It starts by generating a lambda schedule, then runs
    the annihilation, equilibration, and production MD simulations for each
    lambda window. Finally, it analyzes the results to calculate the free energy.

    The ligand must be the first residue in the complex.

    Parameters
    ----------
    name : str, optional
        The name of the flow instance. Default: "lambda_runs".
    nlambdas : int, optional
        The number of lambda windows to use. Default: 12.
    schedule : str, optional
        The lambda schedule to use. Default: "s2inverse".
    restraint_mask : str
        The Amber mask for applying restraints during the simulations.
    restraint_wt : int
        The weight for the restraints. Default: 5.
    nstlim : int
        The number of steps for the AFE equilibration runs. Default: 100000.
    numexchg : int
        The number of exchange attempts for the production run. Default: 10000.
    nmropt: bool
        If True, uses NMR restraints for the complex system. Default: False.
    skippable : bool, optional
        If True, allows individual worknodes to be skipped if their outputs
        already exist. Default: True.
    """

    def __init__(
        self,
        name: str = "abfe1",
        *,
        nlambdas: int = 12,
        schedule: str = "s2inverse",
        heating_restraint_mask: str,
        heating_restraint_wt: int = 5,
        restraint_mask: Optional[str] = None,
        restraint_wt: Optional[int] = None,
        nstlim: int = 100000,
        nstlim_pdt: int = 125,
        numexchg: int = 10000,
        nmropt: bool = False,
        max_systems_binder: int = 1,
        max_systems_complex: int = 1,
        skippable: bool = True,
    ):
        super().__init__(name)

        # Filter for the final relaxed structures and topologies
        wnf_binder_top = WorkNodeFilter(f"wnf_binder_top_{name}", artifact_types=(BaseBinderTopologyFile,))
        wnf_binder_rst = WorkNodeFilter(f"wnf_binder_rst_{name}", artifact_types=(BaseBinderStructureFile,))
        wnf_complex_top = WorkNodeFilter(f"wnf_complex_top_{name}", artifact_types=(BaseComplexTopologyFile,))
        wnf_complex_rst = WorkNodeFilter(f"wnf_complex_rst_{name}", artifact_types=(BaseComplexStructureFile,))
        wnf_complex_nmr_restraints = WorkNodeFilter("wnf_complex_nmr_restraints", artifact_types=(BoreschRestraints,))
        restrained_str = "_restrained" if restraint_mask is not None and restraint_wt is not None else ""
        nmropt_str = "_nmropt" if nmropt else ""

        # Lambda schedule generation
        qls = QuickLambdaSchedule(wnid="qls", nlambdas=nlambdas, schedule=schedule)

        # Annihilation step
        anhilate_params = AnhilateParameters(
            timask1=":1", timask2="", scmask1=":1", scmask2="", restraintmask=restraint_mask, restraint_wt=restraint_wt
        )
        anhilate_binder = LambdaAnhilation(
            wnid="anhilate_binder",
            mdin_template="min_icfe",
            mdparameters=anhilate_params,
            engine="pmemd.cuda",
            skippable=skippable,
        )

        anhilate_complex = LambdaAnhilation(
            wnid="anhilate_complex",
            mdin_template=f"min_icfe{restrained_str}{nmropt_str}",
            mdparameters=anhilate_params,
            engine="pmemd.cuda",
            skippable=skippable,
        )

        # Heating
        heat_params = LambdaParameters(
            nstlim=nstlim,
            irest=0,
            ntx=1,
            timask1=":1",
            timask2="",
            scmask1=":1",
            scmask2="",
            iwrap=0,
            dt=0.001,
            tempi=100,
            temp0=298,
            restraintmask=heating_restraint_mask,
            restraint_wt=heating_restraint_wt,
        )
        # Create reference structures
        crs_binder_heat = CreateReferenceStructure(wnid="crs_binder_heat", state=0.0)
        crs_complex_heat = CreateReferenceStructure(wnid="crs_complex_heat", state=0.0)

        heat_binder = LambdaMDRun(
            wnid="heat_binder",
            mdin_template="md_icfe_varying",
            engine="pmemd.cuda.MPI",
            mdparameters=heat_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )
        heat_complex = LambdaMDRun(
            wnid="heat_complex",
            mdin_template=f"md_icfe{restrained_str}{nmropt_str}_varying",
            ifmbar=True,
            engine="pmemd.cuda.MPI",
            mdparameters=heat_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        ### Equilibration ###
        # 1 #
        equil_params = LambdaParameters(
            nstlim=nstlim,
            irest=1,
            ntx=5,
            timask1=":1",
            timask2="",
            scmask1=":1",
            scmask2="",
            iwrap=0,
            dt=0.001,
            numexchg=numexchg,
        )
        if restraint_mask != "":
            equil_params = attrs.evolve(equil_params, restraintmask=restraint_mask, restraint_wt=restraint_wt)
        crs_binder_eq1 = CreateReferenceStructure(wnid="crs_binder_eq1", state=0.0)
        crs_complex_eq1 = CreateReferenceStructure(wnid="crs_complex_eq1", state=0.0)

        equil1_binder = LambdaMDRun(
            wnid="equil1_binder",
            mdin_template="md_icfe",
            engine="pmemd.cuda.MPI",
            mdparameters=equil_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )
        equil1_complex = LambdaMDRun(
            wnid="equil1_complex",
            mdin_template=f"md_icfe{restrained_str}{nmropt_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=equil_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        # 2 #
        equil_params = attrs.evolve(equil_params, dt=0.002)
        crs_binder_eq2 = CreateReferenceStructure(wnid="crs_binder_eq2", state=0.0)
        crs_complex_eq2 = CreateReferenceStructure(wnid="crs_complex_eq2", state=0.0)

        equil2_binder = LambdaMDRun(
            wnid="equil2_binder",
            mdin_template="md_icfe",
            engine="pmemd.cuda.MPI",
            mdparameters=equil_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )
        equil2_complex = LambdaMDRun(
            wnid="equil2_complex",
            mdin_template=f"md_icfe{restrained_str}{nmropt_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=equil_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )
        # 3 #
        equil_params = attrs.evolve(equil_params, dt=0.004)
        crs_binder_eq3 = CreateReferenceStructure(wnid="crs_binder_eq3", state=0.0)
        crs_complex_eq3 = CreateReferenceStructure(wnid="crs_complex_eq3", state=0.0)

        equil3_binder = LambdaMDRun(
            wnid="equil3_binder",
            mdin_template="md_icfe",
            engine="pmemd.cuda.MPI",
            mdparameters=equil_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )
        equil3_complex = LambdaMDRun(
            wnid="equil3_complex",
            mdin_template=f"md_icfe{restrained_str}{nmropt_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=equil_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        ### Production ###
        # Create reference structures
        crs_binder_pdt = CreateReferenceStructure(wnid="crs_binder_pdt", state=0.0)
        crs_complex_pdt = CreateReferenceStructure(wnid="crs_complex_pdt", state=0.0)
        pdt_params = attrs.evolve(equil_params, nstlim=nstlim_pdt,)

        pdt_binder = LambdaMDRun(
            wnid="pdt_binder",
            mdin_template="ti_exch_mbar",
            ifmbar=True,
            exchange=True,
            engine="pmemd.cuda.MPI",
            mdparameters=pdt_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )
        pdt_complex = LambdaMDRun(
            wnid="pdt_complex",
            mdin_template=f"ti_exch_mbar{restrained_str}{nmropt_str}",
            ifmbar=True,
            exchange=True,
            engine="pmemd.cuda.MPI",
            mdparameters=pdt_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        # Post-processing and analysis
        a2d_binder = Amber2Dats(wnid="a2d_binder", environment="aq", trial=1, target=False, skippable=False)
        a2d_complex = Amber2Dats(wnid="a2d_complex", environment="com", trial=1, target=True, skippable=False)
        xml = GetXML(wnid="get_xml", skippable=False)
        mbar = EdgeMBAR(wnid="edge_mbar", skippable=False)

        # Add nodes to the DAG
        self.dag.add_nodes_from(
            [
                wnf_binder_top,
                wnf_binder_rst,
                wnf_complex_top,
                wnf_complex_rst,
                qls,
                anhilate_binder,
                anhilate_complex,
                crs_binder_heat,
                crs_complex_heat,
                heat_binder,
                heat_complex,
                crs_binder_eq1,
                crs_complex_eq1,
                equil1_binder,
                equil1_complex,
                crs_binder_eq2,
                crs_complex_eq2,
                equil2_binder,
                equil2_complex,
                crs_binder_eq3,
                crs_complex_eq3,
                equil3_binder,
                equil3_complex,
                crs_binder_pdt,
                crs_complex_pdt,
                pdt_binder,
                pdt_complex,
                a2d_binder,
                a2d_complex,
                xml,
                mbar,
            ]
        )
        if nmropt:
            self.dag.add_node(wnf_complex_nmr_restraints)

        # Connect the workflow
        self.dag.add_edge(self.root, wnf_binder_top)
        self.dag.add_edge(self.root, wnf_binder_rst)
        self.dag.add_edge(self.root, wnf_complex_top)
        self.dag.add_edge(self.root, wnf_complex_rst)
        self.dag.add_edge(self.root, qls)
        if nmropt:
            self.dag.add_edge(self.root, wnf_complex_nmr_restraints)

        # Binder path
        # Anhilation
        self.dag.add_edge(wnf_binder_top, anhilate_binder)
        self.dag.add_edge(wnf_binder_rst, anhilate_binder)
        self.dag.add_edge(qls, anhilate_binder)
        # Heating
        self.dag.add_edge(anhilate_binder, crs_binder_heat)
        self.dag.add_edge(anhilate_binder, heat_binder)
        self.dag.add_edge(crs_binder_heat, heat_binder)
        # Equilibration 1
        self.dag.add_edge(heat_binder, crs_binder_eq1)
        self.dag.add_edge(heat_binder, equil1_binder)
        self.dag.add_edge(crs_binder_heat, equil1_binder)
        # Equilibration 2
        self.dag.add_edge(equil1_binder, crs_binder_eq2)
        self.dag.add_edge(equil1_binder, equil2_binder)
        self.dag.add_edge(crs_binder_eq2, equil2_binder)
        # Equilibration 3
        self.dag.add_edge(equil2_binder, crs_binder_eq3)
        self.dag.add_edge(equil2_binder, equil3_binder)
        self.dag.add_edge(crs_binder_eq3, equil3_binder)
        # Production
        self.dag.add_edge(equil3_binder, crs_binder_pdt)
        self.dag.add_edge(equil3_binder, pdt_binder)
        self.dag.add_edge(crs_binder_pdt, pdt_binder)

        # Complex path
        # Anhilation
        if nmropt:
            self.dag.add_edge(wnf_complex_nmr_restraints, anhilate_complex)
        self.dag.add_edge(wnf_complex_top, anhilate_complex)
        self.dag.add_edge(wnf_complex_rst, anhilate_complex)
        self.dag.add_edge(qls, anhilate_complex)
        # Heating
        self.dag.add_edge(anhilate_complex, crs_complex_heat)
        self.dag.add_edge(anhilate_complex, heat_complex)
        self.dag.add_edge(crs_complex_heat, heat_complex)
        # Equilibration 1
        self.dag.add_edge(heat_complex, crs_complex_eq1)
        self.dag.add_edge(heat_complex, equil1_complex)
        self.dag.add_edge(crs_complex_heat, equil1_complex)
        # Equilibration 2
        self.dag.add_edge(equil1_complex, crs_complex_eq2)
        self.dag.add_edge(equil1_complex, equil2_complex)
        self.dag.add_edge(crs_complex_eq2, equil2_complex)
        # Equilibration 3
        self.dag.add_edge(equil2_complex, crs_complex_eq3)
        self.dag.add_edge(equil2_complex, equil3_complex)
        self.dag.add_edge(crs_complex_eq3, equil3_complex)
        # Production
        self.dag.add_edge(equil3_complex, crs_complex_pdt)
        self.dag.add_edge(equil3_complex, pdt_complex)
        self.dag.add_edge(crs_complex_pdt, pdt_complex)

        # Analysis path
        self.dag.add_edge(pdt_binder, a2d_binder)
        self.dag.add_edge(pdt_complex, a2d_complex)
        self.dag.add_edge(a2d_binder, xml)
        self.dag.add_edge(a2d_complex, xml)
        self.dag.add_edge(xml, mbar)
        self.dag.add_edge(mbar, self.leaf)
