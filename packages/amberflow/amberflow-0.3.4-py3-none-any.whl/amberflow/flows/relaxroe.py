from typing import Optional

import attrs

from amberflow.flows import BaseFlow
from amberflow.worknodes import MDRun, WorkNodeFilter
from amberflow.artifacts import (
    MinRestrainedParameters,
    HeatingParameters,
    MDRestrainedParameters,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    BaseBinderStructureFile,
    BaseComplexStructureFile,
    MDParameters,
)

__all__ = ("FlowRelaxRoe",)


class FlowRelaxRoe(BaseFlow):
    """
    A flow for an MD relaxation protocol.

    This flow runs a relaxation protocol on a pair of complex and ligand
    systems. The protocol involves initial minimization, gradual heating,
    density equilibration, and a series of steps where positional
    restraints are slowly removed. This is loosely based on the protocol
    described by Roe [1].

    Parameters
    ----------
    name : str, optional
        The name of the flow instance, by default "relaxroe".
    full_restraint_mask : str
        Amber mask for applying strong restraints on the whole solute during
        the initial clash-fixing minimization.
    noh_restraint_mask : str
        Amber mask for applying restraints on all heavy atoms during heating,
        density equilibration, and initial relaxation stages.
    strong_restraint_wt : int, optional
        The weight (in kcal/mol·Å²) for the strong heavy-atom restraints,
        by default 50.
    bb_restraint_mask : str
        Amber mask for applying restraints on the protein backbone during the
        final relaxation stage.
    bb_restraint_wt : int, optional
        The weight (in kcal/mol·Å²) for the final backbone restraints,
        by default 5.
    relax_weights : tuple[int], optional
        A tuple of integers representing the restraint weights to be used
        in the gradual relaxation stages, by default (25, 10, 5, 2, 1).
    restraint_mask : str, optional
        An optional Amber mask to apply during the final free MD run.
    restraint_wt : int, optional
        The restraint weight for the optional final restraint mask.
    nstlim : int, optional
        The number of MD steps for most of the relaxation stages,
        by default 50000.
    nstlim_density_equilibration : int, optional
        The number of MD steps for the density equilibration stages
        by default 25000.
    maxcyc : int, optional
        The maximum number of minimization cycles, by default 1000.
    ncyc : int, optional
        The number of steepest descent minimization cycles, by default 100.
    skippable : bool, optional
        If True, allows individual worknodes within the flow to be skipped
        if their outputs already exist, by default True.

    References
    ----------
    1. Amber tutorial: https://ambermd.org/tutorials/basic/tutorial13/index.php
    2. Daniel R. Roe, Bernard R. Brooks;
       A protocol for preparing explicitly solvated systems for stable molecular dynamics simulations.
       J. Chem. Phys. 7 August 2020; 153 (5): 054123. https://doi.org/10.1063/5.0013849
    """

    def __init__(
        self,
        name: str = "relaxroe",
        *,
        full_restraint_mask: str,
        noh_restraint_mask: str,
        strong_restraint_wt: int = 50,
        bb_restraint_mask: str,
        bb_restraint_wt: int = 5,
        relax_weights: tuple[int] = (25, 10, 5, 2, 1),
        restraint_mask: Optional[str] = None,
        restraint_wt: Optional[int] = None,
        nstlim: int = 50000,
        nstlim_density_equilibration: int = 25000,
        maxcyc: int = 1000,
        ncyc: int = 100,
        density_equilibration_steps: int = 5,
        skippable: bool = True,
    ):
        super().__init__(name)
        if density_equilibration_steps < 1:
            raise ValueError("density_equilibration_steps must be at least 1.")

        # Filter initial artifacts
        wnf_binder_top = WorkNodeFilter("wnf_binder_top", artifact_types=(BaseBinderTopologyFile,), skippable=skippable)
        wnf_binder_rst = WorkNodeFilter(
            "wnf_binder_rst", artifact_types=(BaseBinderStructureFile,), skippable=skippable
        )
        wnf_complex_top = WorkNodeFilter(
            "wnf_complex_top", artifact_types=(BaseComplexTopologyFile,), skippable=skippable
        )
        wnf_complex_rst = WorkNodeFilter(
            "wnf_complex_rst",
            artifact_types=(BaseComplexStructureFile,),
            skippable=skippable,
        )

        # Relaxation protocol steps
        # Step 0: Strong restraints on heavy atoms
        clash0_params = MinRestrainedParameters(
            ncyc=50, maxcyc=200, restraintmask=full_restraint_mask, restraint_wt=100
        )
        clash_fix_binder = MDRun(
            "clash_fix_binder",
            mdin_template="min_restrained",
            mdparameters=clash0_params,
            engine="pmemd",
            skippable=skippable,
        )
        clash_fix_complex = MDRun(
            "clash_fix_complex",
            mdin_template="min_restrained",
            mdparameters=clash0_params,
            engine="pmemd",
            skippable=skippable,
        )

        # Step 1: Minimize heavy atoms
        min1_params = MinRestrainedParameters(
            restraintmask=noh_restraint_mask,
            maxcyc=maxcyc,
            ncyc=ncyc,
            restraint_wt=strong_restraint_wt,
        )
        min1_binder = MDRun(
            "resmin_binder",
            mdin_template="min_restrained",
            mdparameters=min1_params,
            skippable=skippable,
        )
        min1_complex = MDRun(
            "resmin_complex",
            mdin_template="min_restrained",
            mdparameters=min1_params,
            skippable=skippable,
        )

        # Step 2: Heat the system
        heat2_params = HeatingParameters(
            nstlim=nstlim,
            restraintmask=noh_restraint_mask,
            restraint_wt=strong_restraint_wt,
        )
        heat2_binder = MDRun(
            "heat2_binder",
            mdin_template="md_restrained_varying",
            mdparameters=heat2_params,
            skippable=skippable,
        )
        heat2_complex = MDRun(
            "heat2_complex",
            mdin_template="md_restrained_varying",
            mdparameters=heat2_params,
            skippable=skippable,
        )

        # Step 3: Density equilibration
        density_equilibration_steps_nodes = []
        i = 3
        for step in range(density_equilibration_steps):
            density_params = MDRestrainedParameters(
                nstlim=nstlim_density_equilibration,  # Reduced nstlim for density equilibration, so pmemd.cuda doesn't complain
                dt=0.001,
                gamma_ln=2.0,
                restraintmask=noh_restraint_mask,
                restraint_wt=strong_restraint_wt,
                cut = 12.0,
            )
            density_binder = MDRun(
                f"density{i+step}_binder",
                mdin_template="md_restrained",
                mdparameters=density_params,
                skippable=skippable,
            )
            density_complex = MDRun(
                f"density{i+step}_complex",
                mdin_template="md_restrained",
                mdparameters=density_params,
                skippable=skippable,
            )
            density_equilibration_steps_nodes.append((density_binder, density_complex))

        # Step 4: Gradually reduce restraints
        md_nodes = []
        i += density_equilibration_steps
        for i, wt in enumerate(relax_weights, 4):
            md_params = MDRestrainedParameters(
                nstlim=nstlim,
                dt=0.001,
                gamma_ln=4.0,
                restraintmask=noh_restraint_mask,
                restraint_wt=wt,
            )
            step_binder = MDRun(
                f"lower{i}_binder",
                mdin_template="md_restrained",
                mdparameters=md_params,
                skippable=skippable,
            )
            step_complex = MDRun(
                f"lower{i}_complex",
                mdin_template="md_restrained",
                mdparameters=md_params,
                skippable=skippable,
            )
            md_nodes.append((step_binder, step_complex))

        # Step 5: Final relaxation with backbone restraints
        i += 1
        final_params = MDRestrainedParameters(
            nstlim=nstlim,
            dt=0.002,
            gamma_ln=5.0,
            ntwx=250,
            restraintmask=bb_restraint_mask,
            restraint_wt=bb_restraint_wt,
        )
        final_binder = MDRun(
            f"free{i}_binder",
            mdin_template="md_restrained",
            mdparameters=final_params,
            skippable=skippable,
        )
        final_complex = MDRun(
            f"free{i}_complex",
            mdin_template="md_restrained",
            mdparameters=final_params,
            skippable=skippable,
        )
        # Step 6: Free MD
        i += 1
        free_params = MDParameters(
            nstlim=nstlim,
            dt=0.004,
            gamma_ln=5.0,
            ntwx=250,
        )
        if restraint_mask is not None and restraint_wt is not None:
            free_params = attrs.evolve(free_params, restraintmask=restraint_mask, restraint_wt=restraint_wt)
            mdin_template = "md"
        else:
            mdin_template = "md_restrained"

        free_binder = MDRun(
            f"free{i}_binder",
            mdin_template=mdin_template,
            mdparameters=free_params,
            skippable=skippable,
        )
        free_complex = MDRun(
            f"free{i}_complex",
            mdin_template=mdin_template,
            mdparameters=free_params,
            skippable=skippable,
        )

        # Add nodes to DAG
        self.dag.add_nodes_from(
            [
                wnf_binder_top,
                wnf_binder_rst,
                wnf_complex_top,
                wnf_complex_rst,
                clash_fix_binder,
                clash_fix_complex,
                min1_binder,
                min1_complex,
                heat2_binder,
                heat2_complex,
                final_binder,
                final_complex,
                free_binder,
                free_complex,
            ]
        )
        for step_binder, step_complex in md_nodes:
            self.dag.add_node(step_binder)
            self.dag.add_node(step_complex)

        # Connect the workflow
        self.dag.add_edge(self.root, wnf_binder_top)
        self.dag.add_edge(self.root, wnf_binder_rst)
        self.dag.add_edge(self.root, wnf_complex_top)
        self.dag.add_edge(self.root, wnf_complex_rst)

        # Binder path
        self.dag.add_edge(wnf_binder_top, clash_fix_binder)
        self.dag.add_edge(wnf_binder_rst, clash_fix_binder)
        self.dag.add_edge(clash_fix_binder, min1_binder)
        self.dag.add_edge(min1_binder, heat2_binder)
        # Density equilibration steps may vary
        previous_binder_step = heat2_binder
        for step_binder, _ in density_equilibration_steps_nodes:
            self.dag.add_edge(previous_binder_step, step_binder)
            previous_binder_step = step_binder

        # Restraints relaxation steps may vary
        for step_binder, _ in md_nodes:
            self.dag.add_edge(previous_binder_step, step_binder)
            previous_binder_step = step_binder
        self.dag.add_edge(previous_binder_step, final_binder)
        self.dag.add_edge(final_binder, free_binder)

        # Complex path
        self.dag.add_edge(wnf_complex_top, clash_fix_complex)
        self.dag.add_edge(wnf_complex_rst, clash_fix_complex)
        self.dag.add_edge(clash_fix_complex, min1_complex)
        self.dag.add_edge(min1_complex, heat2_complex)
        # Density equilibration steps may vary
        previous_complex_step = heat2_complex
        for _, step_complex in density_equilibration_steps_nodes:
            self.dag.add_edge(previous_complex_step, step_complex)
            previous_complex_step = step_complex

        # Restraints relaxation steps may vary
        for _, step_complex in md_nodes:
            self.dag.add_edge(previous_complex_step, step_complex)
            previous_complex_step = step_complex
        self.dag.add_edge(previous_complex_step, final_complex)
        self.dag.add_edge(final_complex, free_complex)

        # Connect to leaf
        self.dag.add_edge(free_binder, self.leaf)
        self.dag.add_edge(free_complex, self.leaf)
