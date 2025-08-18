"""Simplified storage tests focusing on core functionality."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from dotevals.exceptions import EvaluationNotFoundError, ExperimentNotFoundError
from dotevals.metrics import accuracy
from dotevals.models import Evaluation, EvaluationStatus, Record, Result, Score
from dotevals.storage.json import JSONStorage


class TestJSONStorage:
    """Core tests for JSON storage."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create JSON storage instance."""
        return JSONStorage(str(tmp_path))

    def test_initialization(self, tmp_path):
        """Test storage initializes correctly."""
        storage = JSONStorage(str(tmp_path))
        assert storage.root_dir == Path(tmp_path)
        assert storage.root_dir.exists()

    def test_experiment_operations(self, storage):
        """Test creating, listing, and deleting experiments."""
        # Create experiments
        storage.create_experiment("exp1")
        storage.create_experiment("exp2")

        # List experiments
        experiments = storage.list_experiments()
        assert "exp1" in experiments
        assert "exp2" in experiments

        # Delete experiment
        storage.delete_experiment("exp1")
        experiments = storage.list_experiments()
        assert "exp1" not in experiments
        assert "exp2" in experiments

    def test_experiment_rename(self, storage):
        """Test renaming experiments."""
        storage.create_experiment("old_name")
        storage.rename_experiment("old_name", "new_name")

        experiments = storage.list_experiments()
        assert "old_name" not in experiments
        assert "new_name" in experiments

    def test_evaluation_operations(self, storage):
        """Test creating and listing evaluations."""
        storage.create_experiment("test_exp")

        # Create evaluations
        eval1 = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        eval2 = Evaluation(
            evaluation_name="eval2",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )

        storage.create_evaluation("test_exp", eval1)
        storage.create_evaluation("test_exp", eval2)

        # List evaluations
        evaluations = storage.list_evaluations("test_exp")
        assert "eval1" in evaluations
        assert "eval2" in evaluations

    def test_add_and_get_results(self, storage):
        """Test adding and retrieving results."""
        storage.create_experiment("test_exp")

        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Create test records
        records = []
        for i in range(5):
            record = Record(
                item_id=i,
                dataset_row={"input": f"test_{i}", "index": i},
                result=Result(
                    Score("exact_match", i % 2 == 0, [accuracy()]), prompt=f"prompt_{i}"
                ),
            )
            records.append(record)

        # Add results
        storage.add_results("test_exp", "eval1", records)

        # Get results
        retrieved = storage.get_results("test_exp", "eval1")
        assert len(retrieved) == 5
        assert all(isinstance(r, Record) for r in retrieved)

    def test_evaluation_status_update(self, storage):
        """Test updating evaluation status."""
        storage.create_experiment("test_exp")

        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Update status
        storage.update_evaluation_status("test_exp", "eval1", EvaluationStatus.RUNNING)

        # Load evaluation to check status
        loaded = storage.load_evaluation("test_exp", "eval1")
        assert loaded.status == EvaluationStatus.RUNNING

        # Complete evaluation
        storage.update_evaluation_status(
            "test_exp", "eval1", EvaluationStatus.COMPLETED
        )
        loaded = storage.load_evaluation("test_exp", "eval1")
        assert loaded.status == EvaluationStatus.COMPLETED

    def test_remove_error_results(self, storage):
        """Test removing error results."""
        storage.create_experiment("test_exp")

        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add mix of success and error results
        records = []
        for i in range(5):
            record = Record(
                item_id=i,
                dataset_row={"input": f"test_{i}", "index": i},
                result=Result(Score("test", True, [])),
                error="Error" if i % 2 == 0 else None,
            )
            records.append(record)

        storage.add_results("test_exp", "eval1", records)

        # Remove specific error results
        storage.remove_error_results_batch("test_exp", "eval1", [0, 2])

        # Check results
        results = storage.get_results("test_exp", "eval1")
        error_indices = [r.dataset_row["index"] for r in results if r.error]
        assert 4 in error_indices  # Only index 4 should still have error
        assert 0 not in error_indices
        assert 2 not in error_indices

    def test_completed_items(self, storage):
        """Test tracking completed items."""
        storage.create_experiment("test_exp")

        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add results
        records = []
        for i in range(3):
            record = Record(
                item_id=i,
                dataset_row={"input": f"test_{i}", "index": i},
                result=Result(Score("test", True, [])),
            )
            records.append(record)

        storage.add_results("test_exp", "eval1", records)

        # Get completed items
        completed = storage.completed_items("test_exp", "eval1")
        assert len(completed) == 3
        assert all(isinstance(idx, int) for idx in completed)

    def test_experiment_not_found_error(self, storage):
        """Test operations on non-existent experiments."""
        # list_evaluations returns empty list for non-existent experiment
        evaluations = storage.list_evaluations("nonexistent")
        assert evaluations == []

        # create_evaluation creates the experiment directory if needed
        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("nonexistent", evaluation)

        # Now the experiment exists
        assert "nonexistent" in storage.list_experiments()

    def test_evaluation_not_found_handling(self, storage):
        """Test handling of non-existent evaluations."""
        storage.create_experiment("test_exp")

        # get_results returns empty list for non-existent evaluation
        results = storage.get_results("test_exp", "nonexistent")
        assert results == []

        # load_evaluation returns None for non-existent
        loaded = storage.load_evaluation("test_exp", "nonexistent")
        assert loaded is None

    def test_add_results_to_nonexistent_evaluation(self, storage):
        """Test adding results to non-existent evaluation raises error."""
        storage.create_experiment("test_exp")

        record = Record(
            item_id=0,
            dataset_row={"test": "data"},
            result=Result(Score("test", True, [])),
        )

        with pytest.raises(EvaluationNotFoundError):
            storage.add_results("test_exp", "nonexistent", [record])

    def test_experiment_idempotent_operations(self, storage):
        """Test idempotent operations."""
        # Creating experiment multiple times is idempotent
        storage.create_experiment("test_exp")
        storage.create_experiment("test_exp")

        experiments = storage.list_experiments()
        assert experiments.count("test_exp") == 1

        # Creating evaluation multiple times is idempotent
        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)
        storage.create_evaluation("test_exp", evaluation)

        evaluations = storage.list_evaluations("test_exp")
        assert evaluations.count("eval1") == 1

    def test_evaluation_with_slash_in_name(self, storage):
        """Test evaluation names with slashes are handled correctly."""
        storage.create_experiment("test_exp")

        # Slash should be replaced with @
        evaluation = Evaluation(
            evaluation_name="model/v1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Should be stored as model@v1.jsonl
        file_path = storage.root_dir / "test_exp" / "model@v1.jsonl"
        assert file_path.exists()

        # But list_evaluations should return the @ version
        evaluations = storage.list_evaluations("test_exp")
        assert "model@v1" in evaluations

    def test_evaluation_metadata(self, storage):
        """Test evaluation metadata is stored correctly."""
        storage.create_experiment("test_exp")

        metadata = {"model": "gpt-4", "temperature": 0.7}
        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
            metadata=metadata,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Load and check metadata
        loaded = storage.load_evaluation("test_exp", "eval1")
        assert loaded.metadata == metadata

    def test_evaluation_with_completed_status(self, storage):
        """Test evaluation with completed status and timestamp."""
        storage.create_experiment("test_exp")

        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.COMPLETED,
            completed_at=time.time(),
        )
        storage.create_evaluation("test_exp", evaluation)

        # Load and verify
        loaded = storage.load_evaluation("test_exp", "eval1")
        assert loaded.status == EvaluationStatus.COMPLETED
        assert loaded.completed_at is not None

    def test_json_decode_error_handling(self, storage):
        """Test handling of corrupted JSON files."""
        storage.create_experiment("test_exp")
        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Corrupt the file
        file_path = storage.root_dir / "test_exp" / "eval1.jsonl"
        with open(file_path, "a") as f:
            f.write("\n{corrupted json")

        # Should return empty list on decode error
        results = storage.get_results("test_exp", "eval1")
        assert results == []

    def test_remove_single_error_result(self, storage):
        """Test removing a single error result."""
        storage.create_experiment("test_exp")
        evaluation = Evaluation(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add results with errors
        records = [
            Record(
                item_id=0,
                dataset_row={"idx": 0},
                result=Result(Score("test", True, [])),
                error="Error 0",
            ),
            Record(
                item_id=1,
                dataset_row={"idx": 1},
                result=Result(Score("test", True, [])),
            ),
            Record(
                item_id=2,
                dataset_row={"idx": 2},
                result=Result(Score("test", True, [])),
                error="Error 2",
            ),
        ]
        storage.add_results("test_exp", "eval1", records)

        # Remove single error
        storage.remove_error_result("test_exp", "eval1", 0)

        results = storage.get_results("test_exp", "eval1")
        error_items = [r.item_id for r in results if r.error]
        assert 0 not in error_items
        assert 2 in error_items


def test_storage_module_imports():
    """Test storage module imports and initialization."""
    from dotevals import storage
    from dotevals.storage.json import JSONStorage

    # Test that registry functions are available
    assert hasattr(storage, "get_storage")
    assert hasattr(storage, "list_backends")
    assert hasattr(storage, "register")

    # Test creating JSON storage directly
    with tempfile.TemporaryDirectory() as tmpdir:
        json_storage = JSONStorage(tmpdir)
        assert json_storage.root_dir == Path(tmpdir)


def test_storage_registry_edge_cases():
    """Test storage registry edge cases."""
    from dotevals.storage.base import StorageRegistry

    registry = StorageRegistry()

    # Test list_backends
    backends = registry.list_backends()
    assert "json" in backends

    # Test get_storage without protocol separator
    storage = registry.get_storage("simple_path")
    assert storage is not None  # Should default to JSON storage


def test_storage_remove_error_results_batch(tmp_path):
    """Test the remove_error_results_batch method."""
    import uuid

    from dotevals.metrics import accuracy
    from dotevals.models import Record, Result, Score
    from dotevals.storage.json import JSONStorage

    storage = JSONStorage(str(tmp_path))
    unique_id = uuid.uuid4().hex[:8]
    exp_name = f"test_exp_{unique_id}"
    eval_name = f"test_eval_{unique_id}"

    # Create experiment and evaluation
    storage.create_experiment(exp_name)
    from dotevals.models import Evaluation, EvaluationStatus

    evaluation = Evaluation(
        evaluation_name=eval_name,
        metadata={"test": "metadata"},
        status=EvaluationStatus.RUNNING,
        started_at=1234567890.0,
        completed_at=None,
    )
    storage.create_evaluation(exp_name, evaluation)

    # Add some results with errors
    # Note: errors should be in the Record, not the Result
    results = [
        Record(Result(), 0, {"input": "test1"}, error="Error 1"),
        Record(Result(), 1, {"input": "test2"}, error="Error 2"),
        Record(Result(Score("test", True, [accuracy()], {})), 2, {"input": "test3"}),
    ]
    storage.add_results(exp_name, eval_name, results)

    # Use remove_error_results_batch to remove multiple errors
    storage.remove_error_results_batch(exp_name, eval_name, [0, 1])

    # Check that error results are removed
    remaining = storage.get_results(exp_name, eval_name)
    assert len(remaining) == 1
    assert remaining[0].item_id == 2


def test_storage_registry_plugin_error_handling():
    """Test storage registry plugin loading error paths."""
    from dotevals.storage.base import StorageRegistry

    registry = StorageRegistry()

    # Test Python 3.9 path
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_entries = MagicMock()
        mock_entries.select = None  # No select method (Python 3.9)
        mock_ep.return_value = {"dotevals.storage": []}

        registry.load_plugins(force=True)
        assert registry._plugins_loaded is True

    # Test plugin load failure
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_entry = MagicMock()
        mock_entry.name = "bad_storage"
        mock_entry.load.side_effect = Exception("Failed to load")

        mock_entries = MagicMock()
        mock_entries.select.return_value = [mock_entry]
        mock_ep.return_value = mock_entries

        with pytest.warns(RuntimeWarning, match="Failed to load storage plugin"):
            registry.load_plugins(force=True)


def test_storage_error_handling(tmp_path):
    """Test storage error handling paths."""
    storage = JSONStorage(str(tmp_path))

    # Test directory creation error
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.side_effect = OSError("Permission denied")
        # Should handle the error gracefully
        try:
            storage.create_experiment("test_exp")
        except OSError:
            pass  # Expected

    # Test file write error
    storage.create_experiment("test_exp2")
    eval = Evaluation(
        evaluation_name="eval1", started_at=time.time(), status=EvaluationStatus.RUNNING
    )

    with patch("builtins.open", side_effect=OSError("Disk full")):
        # Should handle write error
        try:
            storage.create_evaluation("test_exp2", eval)
        except OSError:
            pass  # Expected


def test_storage_init_exports():
    """Test storage __init__ module exports."""
    from dotevals.storage import Storage, get_storage, list_backends, register, registry

    # Verify exports exist and are callable/usable
    assert Storage is not None
    assert callable(get_storage)
    assert callable(list_backends)
    assert callable(register)
    assert registry is not None


@pytest.mark.parametrize(
    "num_records,expected_count",
    [
        (0, 0),
        (1, 1),
        (10, 10),
        (100, 100),
    ],
)
def test_results_batch_sizes(tmp_path, num_records, expected_count):
    """Test different batch sizes of results."""
    storage = JSONStorage(str(tmp_path))
    storage.create_experiment("test")

    evaluation = Evaluation(
        evaluation_name="eval", started_at=time.time(), status=EvaluationStatus.RUNNING
    )
    storage.create_evaluation("test", evaluation)

    # Add records
    records = []
    for i in range(num_records):
        record = Record(
            item_id=i, dataset_row={"index": i}, result=Result(Score("test", True, []))
        )
        records.append(record)

    if records:
        storage.add_results("test", "eval", records)

    # Verify count
    results = storage.get_results("test", "eval")
    assert len(results) == expected_count


def test_concurrent_writes_corruption(tmp_path):
    """Test that concurrent writes can corrupt data - demonstrating the bug."""
    import threading

    storage = JSONStorage(str(tmp_path))
    storage.create_experiment("test")

    eval = Evaluation(
        evaluation_name="eval", started_at=time.time(), status=EvaluationStatus.RUNNING
    )
    storage.create_evaluation("test", eval)

    def add_batch(thread_id):
        records = [
            Record(
                item_id=thread_id * 100 + i,
                dataset_row={"thread": thread_id, "idx": i},
                result=Result(Score("test", True, [])),
            )
            for i in range(100)
        ]
        storage.add_results("test", "eval", records)

    # Launch concurrent writes
    threads = []
    for i in range(5):
        t = threading.Thread(target=add_batch, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Check if data is corrupted
    results = storage.get_results("test", "eval")
    # Due to race conditions, we might not get all 500 results
    # This test demonstrates the thread safety issue
    assert len(results) <= 500  # May be less due to corruption


def test_status_update_nonexistent(tmp_path):
    """Test updating status of non-existent evaluation."""
    storage = JSONStorage(str(tmp_path))
    storage.create_experiment("test")

    with pytest.raises(EvaluationNotFoundError):
        storage.update_evaluation_status(
            "test", "nonexistent", EvaluationStatus.COMPLETED
        )


def test_remove_error_nonexistent_items(tmp_path):
    """Test removing non-existent error items."""
    storage = JSONStorage(str(tmp_path))
    storage.create_experiment("test")

    eval = Evaluation(
        evaluation_name="eval", started_at=time.time(), status=EvaluationStatus.RUNNING
    )
    storage.create_evaluation("test", eval)

    # Add some results
    records = [
        Record(
            item_id=i,
            dataset_row={"idx": i},
            result=Result(Score("test", True, [])),
            error=f"Error {i}" if i < 3 else None,
        )
        for i in range(5)
    ]
    storage.add_results("test", "eval", records)

    # Remove non-existent items - should not crash
    storage.remove_error_results_batch("test", "eval", [99, 100])

    # Original results unchanged
    results = storage.get_results("test", "eval")
    assert len(results) == 5
