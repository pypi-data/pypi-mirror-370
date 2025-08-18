"""Tests for JSON storage internal functionality to achieve targeted coverage."""

import json
import tempfile
from pathlib import Path

import pytest

from dotevals.exceptions import (
    EvaluationNotFoundError,
    ExperimentExistsError,
    ExperimentNotFoundError,
)
from dotevals.models import Evaluation, EvaluationStatus, Record, Result
from dotevals.storage.json import JSONStorage


class TestJSONStorageInternals:
    """Test JSON storage internal functionality."""

    def test_delete_experiment_file_cleanup(self):
        """Test experiment deletion with file cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create an experiment with files
            experiment_name = "test_experiment"
            experiment_path = Path(temp_dir) / experiment_name
            experiment_path.mkdir()

            # Create some files in the experiment directory
            (experiment_path / "eval1.jsonl").write_text('{"test": "data"}')
            (experiment_path / "eval2.jsonl").write_text('{"test": "data2"}')
            (experiment_path / "subfile.txt").write_text("content")

            # Verify files exist
            assert experiment_path.exists()
            assert len(list(experiment_path.iterdir())) == 3

            # Delete the experiment - should clean up all files
            storage.delete_experiment(experiment_name)

            # Verify cleanup
            assert not experiment_path.exists()

    def test_delete_experiment_not_found(self):
        """Test deleting non-existent experiment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Try to delete non-existent experiment
            with pytest.raises(ExperimentNotFoundError):
                storage.delete_experiment("nonexistent")

    def test_create_evaluation_file_already_exists(self):
        """Test create_evaluation when file already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create evaluation record
            evaluation = Evaluation(
                evaluation_name="test_eval",
                metadata={"test": "metadata"},
                started_at=1672531200.0,
                status=EvaluationStatus.COMPLETED,
                completed_at=1672531260.0,
            )

            # Create the evaluation file first time
            storage.create_evaluation("test_exp", evaluation)

            # Verify file was created
            file_path = Path(temp_dir) / "test_exp" / "test_eval.jsonl"
            assert file_path.exists()

            # Read original content
            with open(file_path) as f:
                original_data = json.load(f)

            # Try to create again - should be idempotent (not overwrite)
            modified_evaluation = Evaluation(
                evaluation_name="test_eval",
                metadata={"different": "metadata"},  # Different metadata
                started_at=1672531200.0,
                status=EvaluationStatus.COMPLETED,
                completed_at=1672531260.0,
            )

            storage.create_evaluation("test_exp", modified_evaluation)

            # Verify file wasn't overwritten (idempotent behavior)
            with open(file_path) as f:
                current_data = json.load(f)

            assert current_data == original_data
            assert current_data["metadata"] == {"test": "metadata"}

    def test_add_results_evaluation_not_found(self):
        """Test add_results when evaluation doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create a dummy record
            result = Result(prompt="test prompt")
            record = Record(result=result, item_id=1)

            # Try to add results to non-existent evaluation
            with pytest.raises(EvaluationNotFoundError):
                storage.add_results("test_exp", "nonexistent", [record])

    def test_get_results_file_not_found(self):
        """Test get_results when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Try to get results from non-existent evaluation
            results = storage.get_results("test_exp", "nonexistent_eval")

            # Should return empty list
            assert results == []

    def test_get_results_json_decode_error(self):
        """Test get_results with corrupted JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create experiment directory
            experiment_path = Path(temp_dir) / "test_exp"
            experiment_path.mkdir()

            # Create corrupted JSON file
            eval_file = experiment_path / "corrupted_eval.jsonl"
            eval_file.write_text('{"valid": "header"}\n{invalid json content}')

            # Should return empty list on JSON decode error
            results = storage.get_results("test_exp", "corrupted_eval")
            assert results == []

    def test_rename_experiment_old_not_found(self):
        """Test rename_experiment when old experiment doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            with pytest.raises(ExperimentNotFoundError):
                storage.rename_experiment("nonexistent", "new_name")

    def test_rename_experiment_new_already_exists(self):
        """Test rename_experiment when new name already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create two experiments
            storage.create_experiment("old_exp")
            storage.create_experiment("existing_exp")

            with pytest.raises(ExperimentExistsError):
                storage.rename_experiment("old_exp", "existing_exp")

    def test_rename_experiment_success(self):
        """Test successful rename operation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create experiment with some content
            storage.create_experiment("old_exp")
            old_path = Path(temp_dir) / "old_exp"
            (old_path / "test_file.txt").write_text("content")

            # Rename it
            storage.rename_experiment("old_exp", "new_exp")

            # Verify old directory is gone and new exists
            assert not old_path.exists()
            new_path = Path(temp_dir) / "new_exp"
            assert new_path.exists()
            assert (new_path / "test_file.txt").exists()

    def test_evaluation_name_replacement(self):
        """Test evaluation name slash replacement."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create evaluation with slashes in name
            evaluation = Evaluation(
                evaluation_name="path/to/eval",
                metadata={},
                started_at=1672531200.0,
                status=EvaluationStatus.RUNNING,
            )

            storage.create_evaluation("test_exp", evaluation)

            # Verify file was created with @ replacement
            expected_file = Path(temp_dir) / "test_exp" / "path@to@eval.jsonl"
            assert expected_file.exists()

            # Test that other methods also handle the replacement
            result = Result(prompt="test")
            record = Record(result=result, item_id=1)

            storage.add_results("test_exp", "path/to/eval", [record])
            results = storage.get_results("test_exp", "path/to/eval")
            assert len(results) == 1

    def test_add_results_file_append(self):
        """Test that add_results appends to existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create evaluation first
            evaluation = Evaluation(
                evaluation_name="test_eval",
                metadata={},
                started_at=1672531200.0,
                status=EvaluationStatus.RUNNING,
            )
            storage.create_evaluation("test_exp", evaluation)

            # Add first batch of results
            result1 = Result(prompt="test1")
            record1 = Record(result=result1, item_id=1)
            storage.add_results("test_exp", "test_eval", [record1])

            # Add second batch
            result2 = Result(prompt="test2")
            record2 = Record(result=result2, item_id=2)
            storage.add_results("test_exp", "test_eval", [record2])

            # Verify both results are present
            results = storage.get_results("test_exp", "test_eval")
            assert len(results) == 2

    def test_get_results_skip_empty_lines(self):
        """Test that get_results skips empty lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Create experiment directory and file with empty lines
            experiment_path = Path(temp_dir) / "test_exp"
            experiment_path.mkdir()

            # Create file with proper serialized record format and empty lines
            eval_file = experiment_path / "test_eval.jsonl"
            eval_file.write_text(
                '{"header": "data"}\n'
                '{"item_id": 1, "result": {"prompt": "test1", "scores": [], "error": null, "model_response": null}, "dataset_row": {}, "error": null, "timestamp": 1672531200.0}\n'
                "\n"  # Empty line
                '{"item_id": 2, "result": {"prompt": "test2", "scores": [], "error": null, "model_response": null}, "dataset_row": {}, "error": null, "timestamp": 1672531300.0}\n'
                "\n"  # Another empty line
            )

            # Should skip empty lines and return valid records
            results = storage.get_results("test_exp", "test_eval")
            # Should have 2 records despite empty lines
            assert isinstance(results, list)
            assert len(results) == 2

    def test_load_evaluation_file_not_found(self):
        """Test load_evaluation when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JSONStorage(temp_dir)

            # Try to load non-existent evaluation
            evaluation = storage.load_evaluation("test_exp", "nonexistent")

            # Should return None
            assert evaluation is None
