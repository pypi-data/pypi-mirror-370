import json
import time
from pathlib import Path
from typing import Optional

from dotevals.exceptions import (
    EvaluationNotFoundError,
    ExperimentExistsError,
    ExperimentNotFoundError,
)
from dotevals.models import Evaluation, EvaluationStatus, Record
from dotevals.storage.base import Storage
from dotevals.utils import deserialize_records, serialize_records

__all__ = ["JSONStorage"]


class JSONStorage(Storage):
    """JSON storage backend.

    This backend uses the file structure to store results per experiment
    and per evaluation:

    ```ascii
    experiment_name/
      evaluation_1.jsonl
      evaluation_2.jsonl
    ```

    Results are stored in JSON lines format so we can quickly append new results
    without having to read the files, and easily run evaluations in parallel. The
    first line contains information about the evaluation, such as its name, when
    it was run and the git commit.

    """

    def __init__(self, storage_path: str):
        self.root_dir = Path(storage_path)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def create_experiment(self, experiment_name: str):
        """Create a new experiment by creating a new directory.

        This won't do anything if the experiment already exists.

        """
        experiment_path = self.root_dir / experiment_name
        experiment_path.mkdir(parents=True, exist_ok=True)

    def delete_experiment(self, experiment_name: str):
        """Delete the experiment by deleting the corresponding directory."""
        experiment_path = self.root_dir / experiment_name

        if experiment_path.exists() and experiment_path.is_dir():
            # Delete all files in the experiment directory
            for file in experiment_path.iterdir():
                if file.is_file():
                    file.unlink()
            # Delete the directory
            experiment_path.rmdir()
        else:
            raise ExperimentNotFoundError(experiment_name)

    def rename_experiment(self, old_name: str, new_name: str):
        """Rename the experiment by renaming the corresponding directory"""
        old_dir = self.root_dir / old_name
        new_dir = self.root_dir / new_name

        if not old_dir.exists():
            raise ExperimentNotFoundError(old_name)

        if new_dir.exists():
            raise ExperimentExistsError(new_name)

        old_dir.rename(new_dir)

    def list_experiments(self):
        return [p.name for p in self.root_dir.iterdir() if p.is_dir()]

    def create_evaluation(self, experiment_name: str, evaluation: Evaluation):
        evaluation_name = evaluation.evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Only create if the file doesn't exist (idempotent)
        if not file_path.exists():
            data: dict = {
                "evaluation_name": evaluation.evaluation_name,
                "metadata": evaluation.metadata,
                "started_at": evaluation.started_at,
                "status": evaluation.status.value,
                "completed_at": evaluation.completed_at,
            }

            with open(file_path, "w") as f:
                json.dump(data, f)

    def list_evaluations(self, experiment_name: str) -> list[str]:
        path = self.root_dir / experiment_name
        return [f.stem for f in path.glob("*.jsonl")]

    def add_results(
        self,
        experiment_name: str,
        evaluation_name: str,
        results: list[Record],
    ):
        evaluation_name = evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"

        if not file_path.exists():
            raise EvaluationNotFoundError(experiment_name, evaluation_name)

        with open(file_path, "a") as f:
            data = serialize_records(results)
            for result in data:
                f.write("\n")
                json.dump(result, f)

    def get_results(self, experiment_name: str, evaluation_name: str) -> list[Record]:
        evaluation_name = evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return []

        try:
            results = []
            with open(file_path) as f:
                # Skip the first line (evaluation metadata)
                f.readline()
                # Read all result lines
                for line in f:
                    if line.strip():  # Skip empty lines
                        results.append(json.loads(line))
            return deserialize_records(results)
        except json.JSONDecodeError:
            return []

    def load_evaluation(
        self, experiment_name: str, evaluation_name: str
    ) -> Evaluation | None:
        evaluation_name = evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            first_line = f.readline()
            if first_line:
                data = json.loads(first_line)
                return Evaluation(
                    evaluation_name=data["evaluation_name"],
                    status=EvaluationStatus(data["status"]),
                    started_at=data["started_at"],
                    metadata=data["metadata"],
                    completed_at=data.get("completed_at"),
                )
        return None

    def update_evaluation_status(
        self, experiment_name: str, evaluation_name: str, status
    ):
        evaluation_name = evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            raise EvaluationNotFoundError(experiment_name, evaluation_name)

        # Read all lines
        with open(file_path) as f:
            lines = f.readlines()

        # Update the first line
        if lines:
            eval_data = json.loads(lines[0])
            eval_data["status"] = status.value
            eval_data["completed_at"] = (
                time.time() if status == EvaluationStatus.COMPLETED else None
            )
            lines[0] = json.dumps(eval_data) + "\n"

            # Write back
            with open(file_path, "w") as f:
                f.writelines(lines)

    def remove_error_result(
        self, experiment_name: str, evaluation_name: str, item_id: int
    ):
        """Remove an errored result for a specific item that will be retried."""
        evaluation_name = evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return

        # Read all lines
        with open(file_path) as f:
            lines = f.readlines()

        if len(lines) <= 1:  # Only metadata, no results
            return

        # Filter out the error result for the specified item_id
        new_lines = [lines[0]]  # Keep metadata
        for line in lines[1:]:
            if line.strip():
                result = json.loads(line)
                # Only keep results that are not the error result for this item
                if result.get("item_id") != item_id or result.get("error") is None:
                    new_lines.append(line)

        # Write back the filtered lines
        with open(file_path, "w") as f:
            f.writelines(new_lines)

    def remove_error_results_batch(
        self, experiment_name: str, evaluation_name: str, item_ids: list[int]
    ):
        """Remove multiple errored results efficiently in a single pass."""
        if not item_ids:
            return

        evaluation_name = evaluation_name.replace("/", "@")
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return

        item_ids_set = set(item_ids)

        # Read all lines
        with open(file_path) as f:
            lines = f.readlines()

        if len(lines) <= 1:  # Only metadata, no results
            return

        # Filter out error results for all specified item_ids in one pass
        new_lines = [lines[0]]  # Keep metadata
        for line in lines[1:]:
            if line.strip():
                result = json.loads(line)
                # Only keep results that are not error results for the specified items
                if (
                    result.get("item_id") not in item_ids_set
                    or result.get("error") is None
                ):
                    new_lines.append(line)

        # Write back the filtered lines once
        with open(file_path, "w") as f:
            f.writelines(new_lines)

    def completed_items(self, experiment_name: str, evaluation_name: str) -> list[int]:
        file_path = self.root_dir / experiment_name / f"{evaluation_name}.jsonl"
        if not file_path.exists():
            return []

        with open(file_path) as f:
            # Skip first line (metadata)
            f.readline()
            # Collect item IDs from results, excluding errored items
            item_ids = []
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    # Only include items that completed successfully (no error)
                    if result.get("error") is None:
                        item_ids.append(result["item_id"])
            return item_ids
