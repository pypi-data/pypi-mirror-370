import logging
import math
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

import numpy as np

from truefoundry import ml

try:
    from transformers.integrations.integration_utils import rewrite_logs
    from transformers.trainer_callback import TrainerCallback
except ImportError as e:
    raise ImportError(
        "Importing this module requires `transformers` to be installed"
    ) from e

if TYPE_CHECKING:
    from transformers.trainer_callback import TrainerControl, TrainerState
    from transformers.training_args import TrainingArguments

    from truefoundry.ml import MlFoundryRun

logger = logging.getLogger(__name__)


class TrueFoundryMLCallback(TrainerCallback):
    def __init__(
        self,
        run: "MlFoundryRun",
        log_checkpoints: bool = True,
        checkpoint_artifact_name: Optional[str] = None,
        auto_end_run_on_train_end: bool = False,
        log_training_arguments: bool = True,
    ):
        """
        Args:
            run: The run entity to log metrics to.
            log_checkpoints: Whether to log checkpoints or not, defaults to True.
            checkpoint_artifact_name: The name of the artifact to log checkpoints to, required if log_checkpoints is True.
            auto_end_run_on_train_end: Whether to end the run automatically when training ends, defaults to False.
            log_training_arguments: Whether to log the training arguments or not, defaults to True.
            Usage:
                from transformers import Trainer
                from truefoundry.ml.integrations.huggingface.trainer_callback import TrueFoundryMLCallback
                from truefoundry.ml import get_client

                client = get_client()
                run = client.create_run(ml_repo="my-ml-repo", run_name="my-run", auto_end=False)

                callback = TrueFoundryMLCallback(
                    run=run,
                    log_checkpoints=True,
                    checkpoint_artifact_name="my-checkpoint",
                    auto_end_run_on_train_end=True,
                )

                trainer = Trainer(
                    ...,
                    callbacks=[callback]
                )
        """
        self._run = run
        self._log_checkpoints = log_checkpoints
        if self._log_checkpoints and not checkpoint_artifact_name:
            raise ValueError(
                "`checkpoint_artifact_name` is required when `log_checkpoints` is True"
            )
        self._checkpoint_artifact_name = checkpoint_artifact_name
        self._auto_end_run_on_train_end = auto_end_run_on_train_end
        self._log_training_arguments = log_training_arguments

    @classmethod
    def with_managed_run(
        cls,
        ml_repo: str,
        run_name: Optional[str] = None,
        log_checkpoints: bool = True,
        checkpoint_artifact_name: Optional[str] = None,
        auto_end_run_on_train_end: bool = True,
        log_training_arguments: bool = True,
    ) -> "TrueFoundryMLCallback":
        """
        Args:
            ml_repo: The name of the ML Repository to log metrics and data to.
            run_name: The name of the run, if not provided, a random name will be generated.
            log_checkpoints: Whether to log checkpoints or not, defaults to True.
            checkpoint_artifact_name: The name of the artifact to log checkpoints to, required if log_checkpoints is True.
            auto_end_run_on_train_end: Whether to end the run automatically when training ends, defaults to True.
            log_training_arguments: Whether to log the training arguments or not, defaults to True.
        Usage:
            from transformers import Trainer
            from truefoundry.ml.integrations.huggingface.trainer_callback import TrueFoundryMLCallback

            callback = TrueFoundryMLCallback.with_managed_run(
                ml_repo="my-ml-repo",
                run_name="my-run",
                log_checkpoints=True,
                checkpoint_artifact_name="my-checkpoint",
                auto_end_run_on_train_end=True,
            )
            trainer = Trainer(
                ...,
                callbacks=[callback]
            )
        """
        run = ml.get_client().create_run(
            ml_repo=ml_repo, run_name=run_name, auto_end=False
        )
        return cls(
            run=run,
            log_checkpoints=log_checkpoints,
            checkpoint_artifact_name=checkpoint_artifact_name,
            auto_end_run_on_train_end=auto_end_run_on_train_end,
            log_training_arguments=log_training_arguments,
        )

    def _drop_non_finite_values(self, dct: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in dct.items():
            if isinstance(v, (int, float, np.integer, np.floating)) and math.isfinite(
                v
            ):
                sanitized[k] = v
            else:
                logger.warning(
                    f'Trainer is attempting to log a value of "{v}" of'
                    f' type {type(v)} for key "{k}" as a metric.'
                    " Mlfoundry's log_metric() only accepts finite float and"
                    " int types so we dropped this attribute."
                )
        return sanitized

    @property
    def run(self) -> "MlFoundryRun":
        return self._run

    # noinspection PyMethodOverriding
    def on_log(
        self,
        args: "TrainingArguments",
        state: "TrainerState",
        control: "TrainerControl",
        logs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        logs = logs or {}
        if not state.is_world_process_zero:
            return

        metrics = self._drop_non_finite_values(logs)
        self._run.log_metrics(rewrite_logs(metrics), step=state.global_step)

    def on_save(
        self,
        args: "TrainingArguments",
        state: "TrainerState",
        control: "TrainerControl",
        **kwargs,
    ):
        if not state.is_world_process_zero:
            return

        if not self._log_checkpoints:
            return

        if not self._checkpoint_artifact_name:
            return

        ckpt_dir = f"checkpoint-{state.global_step}"
        artifact_path = os.path.join(args.output_dir, ckpt_dir)
        description = None
        _job_name = os.getenv("TFY_INTERNAL_COMPONENT_NAME")
        _job_run_name = os.getenv("TFY_INTERNAL_JOB_RUN_NAME")
        if _job_name:
            description = f"Checkpoint from job={_job_name} run={_job_run_name}"
        logger.info(f"Uploading checkpoint {ckpt_dir} ...")
        metadata = {}
        for log in state.log_history:
            if isinstance(log, dict) and log.get("step") == state.global_step:
                metadata = log.copy()
        metadata = self._drop_non_finite_values(metadata)
        self._run.log_artifact(
            name=self._checkpoint_artifact_name,
            artifact_paths=[(artifact_path, None)],
            metadata=metadata,
            step=state.global_step,
            description=description,
        )

    def on_train_begin(
        self,
        args: "TrainingArguments",
        state: "TrainerState",
        control: "TrainerControl",
        **kwargs,
    ):
        if self._log_training_arguments:
            training_arguments = args.to_sanitized_dict()
            valid_types = (bool, int, float, str)
            training_arguments = {
                k: v for k, v in training_arguments.items() if type(v) in valid_types
            }
            self._run.log_params(training_arguments)

    def on_train_end(
        self,
        args: "TrainingArguments",
        state: "TrainerState",
        control: "TrainerControl",
        **kwargs,
    ):
        """
        Event called at the end of training.
        """
        if self._auto_end_run_on_train_end:
            self._run.end()
