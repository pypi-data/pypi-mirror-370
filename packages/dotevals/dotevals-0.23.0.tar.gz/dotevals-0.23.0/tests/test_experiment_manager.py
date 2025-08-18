import re
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from dotevals.models import Evaluation, EvaluationStatus, Record, Result, Score
from dotevals.sessions import SessionManager, get_git_commit
from dotevals.storage.json import JSONStorage


@pytest.fixture
def temp_storage_dir(tmp_path):
    """Create a temporary directory for storage tests."""
    return tmp_path


def test_session_manager_init_without_experiment():
    """Test SessionManager initialization without experiment creates ephemeral experiment."""
    manager = SessionManager("eval_test")
    assert manager.storage is not None
    assert manager.current_experiment is not None  # Should create ephemeral experiment

    assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", manager.current_experiment)
    assert manager.evaluation_progress is None


def test_session_manager_init_with_experiment(temp_storage_dir):
    """Test SessionManager initialization with experiment."""
    storage_path = f"json://{temp_storage_dir}"
    experiment_name = "test_experiment"

    manager = SessionManager(
        storage=storage_path,
        experiment_name=experiment_name,
        evaluation_name="test_eval",
    )

    assert manager.current_experiment == experiment_name
    # Check that experiment was created
    experiments = manager.storage.list_experiments()
    assert experiment_name in experiments


@patch("dotevals.sessions.get_git_commit")
def test_start_evaluation(mock_git_commit, temp_storage_dir):
    """Test starting a new evaluation."""
    mock_git_commit.return_value = "abc123"
    storage_path = f"json://{temp_storage_dir}"

    manager = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval"
    )
    manager.start_evaluation()

    assert manager.evaluation_progress is not None
    assert manager.evaluation_progress.evaluation_name == "test_eval"

    # Check that evaluation was created in storage
    loaded_eval = manager.storage.load_evaluation("test_exp", "test_eval")
    assert loaded_eval is not None
    assert loaded_eval.status == EvaluationStatus.RUNNING
    assert loaded_eval.metadata["git_commit"] == "abc123"


def test_resume_evaluation(temp_storage_dir):
    """Test resuming an existing evaluation."""
    storage_path = f"json://{temp_storage_dir}"

    # First, create an evaluation with some results
    manager1 = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval"
    )
    manager1.start_evaluation()

    # Add some results
    score = Score("test_evaluator", True, [], {})
    result = Result(score, prompt="test prompt")
    record = Record(result=result, item_id=0, dataset_row={})
    manager1.add_results([record])

    # Create a new manager and resume
    manager2 = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval"
    )
    manager2.start_evaluation()

    # Should detect it's resuming
    # (In real usage, this would print a message about resuming)


def test_add_results(temp_storage_dir):
    """Test adding results through SessionManager."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval"
    )
    manager.start_evaluation()

    score = Score("test_evaluator", True, [], {})
    result = Result(score, prompt="test prompt")
    record = Record(result=result, item_id=0, dataset_row={})

    manager.add_results([record])

    # Check that results were added
    results = manager.get_results()
    assert len(results) == 1
    assert results[0].item_id == 0

    # Check progress tracking
    assert manager.evaluation_progress.completed_count == 1
    assert manager.evaluation_progress.error_count == 0


def test_add_results_with_errors(temp_storage_dir):
    """Test adding results with errors."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval"
    )
    manager.start_evaluation()

    score = Score("test_evaluator", False, [], {})
    result = Result(score, prompt="test prompt")

    # Create one successful and one failed record
    record1 = Record(result=result, item_id=0, dataset_row={})
    record2 = Record(result=result, item_id=1, dataset_row={}, error="Test error")

    manager.add_results([record1, record2])

    # Check progress tracking
    assert manager.evaluation_progress.completed_count == 2
    assert manager.evaluation_progress.error_count == 1


def test_finish_evaluation(temp_storage_dir):
    """Test finishing an evaluation."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval"
    )
    manager.start_evaluation()

    # Finish successfully
    manager.finish_evaluation(success=True)

    # Check that status was updated
    loaded_eval = manager.storage.load_evaluation("test_exp", "test_eval")
    assert loaded_eval.status == EvaluationStatus.COMPLETED
    assert loaded_eval.completed_at is not None

    # Start another evaluation and finish with failure
    manager2 = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="test_eval2"
    )
    manager2.start_evaluation()
    manager2.finish_evaluation(success=False)

    loaded_eval2 = manager.storage.load_evaluation("test_exp", "test_eval2")
    assert loaded_eval2.status == EvaluationStatus.FAILED


def test_finish_all_evaluations(temp_storage_dir):
    """Test finishing all active evaluations."""
    storage_path = f"json://{temp_storage_dir}"

    # Start multiple evaluations
    manager1 = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="eval1"
    )
    manager2 = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="eval2"
    )
    manager3 = SessionManager(
        storage=storage_path, experiment_name="test_exp", evaluation_name="eval3"
    )

    manager1.start_evaluation()
    manager2.start_evaluation()
    manager3.start_evaluation()

    # Finish all individually since we no longer have finish_all
    manager1.finish_evaluation(success=True)
    manager2.finish_evaluation(success=True)
    manager3.finish_evaluation(success=True)

    # Check all were marked as completed
    for eval_name in ["eval1", "eval2", "eval3"]:
        loaded = manager1.storage.load_evaluation("test_exp", eval_name)
        assert loaded.status == EvaluationStatus.COMPLETED


@patch("subprocess.check_output")
def test_get_git_commit_success(mock_check_output):
    """Test getting git commit when git is available."""
    mock_check_output.return_value = b"abc123def456\n"

    commit = get_git_commit()

    assert commit == "abc123de"  # First 8 characters


@patch("subprocess.check_output")
def test_get_git_commit_failure(mock_check_output):
    """Test getting git commit when git fails."""
    import subprocess

    mock_check_output.side_effect = subprocess.CalledProcessError(1, "git")

    commit = get_git_commit()

    assert commit is None


def test_session_manager_operations_with_ephemeral_experiment():
    """Test SessionManager operations with ephemeral experiment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create session manager without experiment name - creates ephemeral
        session_manager = SessionManager("eval_test", storage=f"json://{temp_dir}")

        # Should have created ephemeral experiment
        assert session_manager.current_experiment is not None
        assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", session_manager.current_experiment)

        # All operations should work with ephemeral experiment
        session_manager = SessionManager(
            storage=f"json://{temp_dir}", evaluation_name="test_eval"
        )
        session_manager.start_evaluation()

        result = Result(prompt="test")
        record = Record(result=result, item_id=0, dataset_row={})
        session_manager.add_results([record])

        results = session_manager.get_results()
        assert len(results) == 1

        session_manager.finish_evaluation(success=True)


def test_session_manager_add_results_without_progress():
    """Test adding results when evaluation_progress is None."""
    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="test_exp",
            evaluation_name="test_eval",
        )

        # Don't call start_evaluation, so evaluation_progress remains None
        session_manager.evaluation_progress = None

        # Create evaluation manually to avoid the start_evaluation logic
        evaluation = Evaluation(
            evaluation_name="test_eval",
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
        )
        session_manager.storage.create_evaluation("test_exp", evaluation)

        # Add results without evaluation_progress
        result = Result(prompt="test")
        record = Record(result=result, item_id=0, dataset_row={})

        # This should work even without evaluation_progress
        session_manager.add_results([record])

        # Verify results were added
        results = session_manager.get_results()
        assert len(results) == 1


def test_ephemeral_experiment_created_when_no_name():
    """Test that ephemeral experiment is created with timestamp when no name provided."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = f"json://{temp_dir}"

        # Create session manager without experiment name
        session_manager = SessionManager("eval_test", storage=storage_path)

        # Should have created an ephemeral experiment
        assert session_manager.current_experiment is not None
        # New simplified logic: experiment name is just timestamp_uuid
        assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", session_manager.current_experiment)

        # Verify experiment was created directly in the specified storage directory
        storage = JSONStorage(temp_dir)
        experiments = storage.list_experiments()
        assert len(experiments) == 1
        # Should contain our generated experiment name
        assert session_manager.current_experiment in experiments


def test_ephemeral_experiment_in_doteval_directory():
    """Test ephemeral experiments are created in .dotevals subdirectory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        doteval_dir = Path(temp_dir) / ".dotevals"
        storage_path = f"json://{doteval_dir}"

        # Create session manager without experiment name
        session_manager = SessionManager("eval_test", storage=storage_path)

        # Should create experiment directly with timestamp_uuid
        timestamp_pattern = re.compile(r"^\d{8}_\d{6}_[a-f0-9]{8}$")
        assert timestamp_pattern.match(session_manager.current_experiment)

        # Verify directory structure
        assert doteval_dir.exists()
        exp_dir = doteval_dir / session_manager.current_experiment
        assert exp_dir.exists()


def test_ephemeral_experiment_timestamp_format():
    """Test that ephemeral experiment timestamp matches expected format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = f"json://{temp_dir}"

        # Create session manager
        before_time = datetime.now()
        session_manager = SessionManager("eval_test", storage=storage_path)
        after_time = datetime.now()

        # Extract timestamp from experiment name (before the UUID part)
        timestamp_str = session_manager.current_experiment.split("_")[:2]
        timestamp_str = "_".join(timestamp_str)

        # Parse timestamp
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

        # Verify timestamp is within expected range (ignoring microseconds)
        assert before_time.replace(microsecond=0) <= timestamp <= after_time


def test_multiple_ephemeral_experiments():
    """Test creating multiple ephemeral experiments."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = f"json://{temp_dir}"

        managers = []
        for i in range(3):
            manager = SessionManager("eval_test", storage=storage_path)
            managers.append(manager)

        # All should have different experiment names
        experiment_names = [m.current_experiment for m in managers]
        assert len(set(experiment_names)) == 3

        # Verify all experiments exist in the specified storage directory
        storage = JSONStorage(temp_dir)
        ephemeral_experiments = storage.list_experiments()
        assert len(ephemeral_experiments) == 3

        # All should have timestamp_uuid format
        for exp in ephemeral_experiments:
            assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", exp)
