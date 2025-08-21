import shutil
from pathlib import Path
from typing import Optional, Any

from amberflow.artifacts import (
    BaseRestartStatesFile,
    ArtifactContainer,
    BaseStructureReferenceFile,
    ArtifactRegistry,
)
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
)
from amberflow.worknodes import worknodehelper, noderesource, BaseSingleWorkNode

__all__ = ("CreateReferenceStructure",)


@noderesource(DEFAULT_RESOURCES_PATH / "mdin")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseRestartStatesFile,),
    output_artifact_types=(BaseStructureReferenceFile,),
)
class CreateReferenceStructure(BaseSingleWorkNode):
    """
    Create a reference structure file out of a set of restart states.
    """

    def __init__(
        self,
        wnid: str,
        *args,
        state: float = "min_icfe_restrained",
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.state = state

    # noinspection DuplicatedCode
    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        cores: Optional[int] = None,
        gpus: tuple[int] = (1,),
        restraints_file: Optional[filepath_t] = None,
        sbatch_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        struct_states = self.input_artifacts["BaseRestartStatesFile"]
        if self.state not in set(struct_states.states.keys()):
            err_msg = f"""State {self.state} not present in input {struct_states}
Available states: {struct_states.states.keys()}"""
            self.logger.error(err_msg)
            raise ValueError(err_msg)
        art_filepath = struct_states.states[self.state]
        # Copy the file to the work directory
        output_filepath = shutil.copy(art_filepath, self.work_dir / art_filepath.name)
        self.output_artifacts = self.fill_output_artifacts(sysname, output_filepath=output_filepath)
        return self.output_artifacts

    def _try_and_skip(self, sysname: str, *, output_filepath: Path) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(self, sysname: str, *, output_filepath: Path) -> ArtifactContainer:
        # TODO: I have to find a better way to do this
        input_art_type_str = self.artifact_map["BaseRestartStatesFile"]
        new_tags = set(self.tags[input_art_type_str])
        new_tags.discard("alchemical")
        new_tags.add("reference")
        out_art = ArtifactRegistry.create_instance_by_filename(output_filepath, tags=tuple(new_tags))

        return ArtifactContainer(sysname, (out_art,))
