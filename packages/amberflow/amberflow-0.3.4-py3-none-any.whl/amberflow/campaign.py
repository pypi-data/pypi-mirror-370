import pickle
import concurrent.futures
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any

from amberflow.pipeline import Pipeline
from amberflow.primitives import BaseCommand


class Campaign:
    """
    Orchestrates the execution of a Pipeline across multiple systems,
    batched and distributed across multiple execution sites.
    """

    def __init__(
        self,
        pipeline: Pipeline,
        sites: List[BaseCommand],
        systems_per_batch: int = 1,
        campaign_work_dir: Path = None,
    ):
        self.pipeline = pipeline
        self.sites = sites
        self.systems_per_batch = systems_per_batch
        self.work_dir = campaign_work_dir or pipeline.cwd / "campaign_work"
        self.work_dir.mkdir(exist_ok=True)
        self.logger = pipeline.logger
        self.checkpoint_path = self.work_dir / "campaign_checkpoint.pkl"

        # This will hold the state of all batches
        self.batches: List[Dict[str, Any]] = []

    def _prepare_batches(self) -> None:
        """Splits systems into batches and initializes self.batches."""
        all_systems = sorted(list(self.pipeline.systems.keys()))
        system_batches = [
            all_systems[i : i + self.systems_per_batch] for i in range(0, len(all_systems), self.systems_per_batch)
        ]

        self.batches = []
        for i, system_group in enumerate(system_batches):
            batch_id = f"batch_{i:03d}"
            batch_dir = self.work_dir / batch_id
            batch_dir.mkdir(exist_ok=True)
            self.batches.append(
                {
                    "id": batch_id,
                    "systems": system_group,
                    "dir": batch_dir,
                    "status": "PENDING",  # PENDING, RUNNING, COMPLETED, FAILED
                }
            )

    def launch(self):
        """
        Launches the campaign, distributing batches across sites.
        """
        # Load state from checkpoint or prepare new batches
        if self.checkpoint_path.exists():
            with open(self.checkpoint_path, "rb") as f:
                self.batches = pickle.load(f)
            self.logger.info("Resuming campaign from checkpoint.")
        else:
            self._prepare_batches()
            self._write_checkpoint()

        # Filter for batches that need to be run
        jobs_to_run = [b for b in self.batches if b["status"] in ("PENDING", "FAILED")]

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.sites)) as executor:
            future_to_batch = {
                executor.submit(self._run_batch, batch, site): batch for batch, site in zip(jobs_to_run, self.sites)
            }

            remaining_jobs = jobs_to_run[len(self.sites) :]

            for future in concurrent.futures.as_completed(future_to_batch):
                completed_batch = future_to_batch[future]
                try:
                    future.result()
                    completed_batch["status"] = "COMPLETED"
                    self.logger.info(f"Batch {completed_batch['id']} completed successfully.")
                except Exception as e:
                    completed_batch["status"] = "FAILED"
                    self.logger.error(f"Batch {completed_batch['id']} failed: {e}")
                finally:
                    # Checkpoint the final status of the completed batch
                    self._write_checkpoint()

                if remaining_jobs:
                    next_job = remaining_jobs.pop(0)
                    # A simple way to find a free site is to assume the pool manages it.
                    # For a more advanced scheduler, you'd track site availability.
                    # Here, we just re-submit to one of the sites.
                    free_site = self.sites[0]  # Simplified for this example
                    new_future = executor.submit(self._run_batch, next_job, free_site)
                    future_to_batch[new_future] = next_job

    def _run_batch(self, batch_info: dict, site: BaseCommand):
        """
        Prepares and runs a single batch on a specific site.
        """
        batch_id = batch_info["id"]
        batch_systems = batch_info["systems"]
        batch_dir = batch_info["dir"]

        self.logger.info(f"Preparing batch {batch_id} for execution on site.")

        # Update status to RUNNING and checkpoint immediately
        batch_info["status"] = "RUNNING"
        self._write_checkpoint()

        sub_pipeline = deepcopy(self.pipeline)
        sub_pipeline.systems = {sys_name: self.pipeline.systems[sys_name] for sys_name in batch_systems}
        root_artifacts = sub_pipeline.artifacts["Root"]
        pruned_root_data = {sys_name: root_artifacts[sys_name] for sys_name in batch_systems}
        root_artifacts._data = pruned_root_data

        final_pipeline = sub_pipeline.setup_new_pipeline(site.executor)

        pickle_fn = batch_dir / "pipeline.pkl"
        with open(pickle_fn, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(final_pipeline, f)

        self.logger.info(f"Executing batch {batch_id}...")
        site.run(
            ["runflow", str(pickle_fn.relative_to(batch_dir))],  # Use relative path for the command
            cwd=batch_dir,
            logger=self.logger,
        )

    def _write_checkpoint(self):
        """Saves the current state of self.batches to the checkpoint file."""
        with open(self.checkpoint_path, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(self.batches, f)
