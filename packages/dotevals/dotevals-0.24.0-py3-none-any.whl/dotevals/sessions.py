import time
import uuid
from datetime import datetime
from typing import Optional, Union

from dotevals.models import Evaluation, EvaluationStatus, Record
from dotevals.storage import Storage, registry


class EvaluationProgress:
    """Runtime progress tracking for an evaluation.

    Used for progress bars.

    """

    def __init__(self, evaluation_name: str) -> None:
        self.evaluation_name = evaluation_name
        self.completed_count = 0
        self.error_count = 0
        self.start_time = time.time()


class SessionManager:
    """Manages experiment lifecycle and storage"""

    def __init__(
        self,
        evaluation_name: str,
        experiment_name: str | None = None,
        storage: Storage | str | None = None,
    ):
        # Get storage instance from path or use provided Storage object
        if isinstance(storage, Storage):
            self.storage = storage
        else:
            self.storage = registry.get_storage(storage)

        self.evaluation_progress: EvaluationProgress | None = None

        # If no experiment name provided, create ephemeral one with timestamp
        if experiment_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            short_uuid = str(uuid.uuid4())[:8]
            experiment_name = f"{timestamp}_{short_uuid}"

        self.current_experiment: str = experiment_name
        self.current_evaluation: str = evaluation_name
        self.storage.create_experiment(experiment_name)

    def start_evaluation(self) -> None:
        """Start or resume an evaluation within the current experiment.

        This method either creates a new evaluation or resumes an existing one.
        If resuming, it reports the number of already completed samples and
        continues from where it left off.

        Side Effects:
            - Creates new evaluation in storage if it doesn't exist
            - Adds Git commit hash to metadata for reproducibility tracking
            - Initializes progress tracking for the evaluation
            - Prints resume message if continuing existing evaluation
        """
        evaluation = self.storage.load_evaluation(
            self.current_experiment, self.current_evaluation
        )

        if evaluation:
            completed_items = self.storage.completed_items(
                self.current_experiment, self.current_evaluation
            )
            print(
                f"{self.current_evaluation}: Resuming from {len(completed_items)} completed samples"
            )
        else:
            git_commit = get_git_commit()
            metadata = {"git_commit": git_commit} if git_commit else {}
            evaluation = Evaluation(
                evaluation_name=self.current_evaluation,
                status=EvaluationStatus.RUNNING,
                started_at=time.time(),
                metadata=metadata,
            )
            self.storage.create_evaluation(self.current_experiment, evaluation)

        self.evaluation_progress = EvaluationProgress(self.current_evaluation)

    def add_results(self, results: list[Record]) -> None:
        """Add evaluation results to storage and update progress tracking.

        Args:
            results: List of Record objects containing evaluation results
        """
        self.storage.add_results(
            self.current_experiment, self.current_evaluation, results
        )

        if self.evaluation_progress:
            for result in results:
                self.evaluation_progress.completed_count += 1
                if result.error is not None:
                    self.evaluation_progress.error_count += 1

    def get_results(self) -> list[Record]:
        """Retrieve all results for the current evaluation.

        Returns:
            List of Record objects containing all results for the evaluation
        """
        return self.storage.get_results(
            self.current_experiment, self.current_evaluation
        )

    def finish_evaluation(self, success: bool = True) -> None:
        """Mark the current evaluation as completed or failed in storage.

        Args:
            success: Whether the evaluation completed successfully (True) or failed (False)
        """
        status = EvaluationStatus.COMPLETED if success else EvaluationStatus.FAILED
        self.storage.update_evaluation_status(
            self.current_experiment, self.current_evaluation, status
        )


def get_git_commit() -> str | None:
    """Get the short Git commit hash of the current repository.

    This function attempts to retrieve the current Git commit hash using
    the git command line tool. It returns the first 8 characters of the
    commit hash for brevity, which is typically sufficient for identification.

    Returns:
        Optional[str]: The first 8 characters of the current Git commit hash,
                      or None if Git is not available or not in a Git repository.

    Examples:
        ```python
        >>> get_git_commit()
        'a1b2c3d4'  # If in a Git repository

        >>> get_git_commit()
        None  # If not in a Git repository or Git not available
        ```

    Note:
        This function is used to track which version of the code was used
        for evaluations, enabling reproducibility and debugging.
    """
    try:
        import subprocess

        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()[:8]
        )
    except subprocess.CalledProcessError:
        return None
