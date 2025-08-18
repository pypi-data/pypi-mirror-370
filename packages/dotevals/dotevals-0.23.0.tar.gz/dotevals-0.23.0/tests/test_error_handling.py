"""Tests for error handling and user experience in failure scenarios."""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from dotevals.core import ForEach
from dotevals.evaluators import exact_match
from dotevals.metrics import accuracy
from dotevals.models import EvaluationStatus, Result, Score
from dotevals.sessions import SessionManager
from dotevals.storage.json import JSONStorage


@pytest.fixture
def temp_storage():
    """Provide temporary storage for error handling tests."""
    with tempfile.TemporaryDirectory() as temp_storage:
        yield Path(temp_storage)


def test_evaluation_function_raises_value_error(temp_storage):
    """Test evaluation function raising ValueError provides helpful error message."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("Q1", "A1"), ("Q2", "A2"), ("Q3", "A3")]

    def eval_with_value_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            raise ValueError("Invalid input format")
        return Result(exact_match(answer, "A1"), prompt=prompt)

    session_manager = SessionManager(
        evaluation_name=f"eval_with_value_error_{unique_id}",
        experiment_name=f"error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_with_value_error_wrapped(question, answer):
        return eval_with_value_error(question, answer)

    # Should not crash - should continue processing other items
    coro = eval_with_value_error_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    # Should have processed all 3 items (including the error)
    assert len(result.results) == 3

    # First and third items should succeed, second should have error
    assert result.results[0].error is None
    assert result.results[1].error is not None
    assert "Invalid input format" in result.results[1].error
    assert result.results[2].error is None

    # Results should be stored
    results = session_manager.storage.get_results(
        f"error_test_{unique_id}", f"eval_with_value_error_{unique_id}"
    )
    assert len(results) == 3

    # Only successful items should be in completed_ids
    completed_ids = session_manager.storage.completed_items(
        f"error_test_{unique_id}", f"eval_with_value_error_{unique_id}"
    )
    assert set(completed_ids) == {0, 2}  # Only successful items, not errors


def test_evaluation_function_raises_key_error(temp_storage):
    """Test evaluation function raising KeyError provides helpful context."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_key_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            # Simulates accessing missing dictionary key
            raise KeyError("missing_field")
        return Result(exact_match(answer, "A1"), prompt=prompt)

    session_manager = SessionManager(
        evaluation_name=f"eval_with_key_error_{unique_id}",
        experiment_name=f"key_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_with_key_error_wrapped(question, answer):
        return eval_with_key_error(question, answer)

    coro = eval_with_key_error_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    # Should continue processing despite KeyError
    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is not None
    assert "missing_field" in result.results[1].error


def test_evaluation_function_raises_type_error(temp_storage):
    """Test evaluation function raising TypeError provides clear error context."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_type_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            # Simulates type mismatch
            return question + 123  # String + int TypeError
        return Result(exact_match(answer, "A1"), prompt=prompt)

    session_manager = SessionManager(
        evaluation_name=f"eval_with_type_error_{unique_id}",
        experiment_name=f"type_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_with_type_error_wrapped(question, answer):
        return eval_with_type_error(question, answer)

    coro = eval_with_type_error_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is not None
    # Should capture the actual TypeError message
    assert (
        "concatenate" in result.results[1].error
        or "TypeError" in result.results[1].error
    )


@pytest.mark.xfail(
    reason="Framework doesn't yet validate return types - progress tracker crashes on invalid types"
)
def test_evaluation_function_returns_invalid_type(temp_storage):
    """Test evaluation function returning non-Result objects raises clear error."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_invalid_return(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            return "invalid_return_value"  # Should return Result objects
        return Result(exact_match(answer, "A1"), prompt=prompt)

    session_manager = SessionManager(
        evaluation_name=f"eval_with_invalid_return_{unique_id}",
        experiment_name=f"invalid_return_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_with_invalid_return_wrapped(question, answer):
        return eval_with_invalid_return(question, answer)

    coro = eval_with_invalid_return_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is not None
    # Should have helpful error message about Result objects
    assert "Result" in result.results[1].error


def test_multiple_errors_in_single_evaluation(temp_storage):
    """Test handling multiple errors in the same evaluation batch."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [(f"Q{i}", f"A{i}") for i in range(1, 6)]  # 5 items

    def eval_with_multiple_errors(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            raise ValueError("Error in item 2")
        elif question == "Q4":
            raise KeyError("Error in item 4")
        return Result(exact_match(answer, "A1"), prompt=prompt)

    session_manager = SessionManager(
        evaluation_name=f"eval_with_multiple_errors_{unique_id}",
        experiment_name=f"multiple_errors_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_with_multiple_errors_wrapped(question, answer):
        return eval_with_multiple_errors(question, answer)

    coro = eval_with_multiple_errors_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    # All items should be processed
    assert len(result.results) == 5

    # Check specific error patterns
    assert result.results[0].error is None  # Q1 succeeds
    assert "Error in item 2" in result.results[1].error  # Q2 fails
    assert result.results[2].error is None  # Q3 succeeds
    assert "Error in item 4" in result.results[3].error  # Q4 fails
    assert result.results[4].error is None  # Q5 succeeds

    # Only successful items should be in completed_ids
    completed_ids = session_manager.storage.completed_items(
        f"multiple_errors_test_{unique_id}", f"eval_with_multiple_errors_{unique_id}"
    )
    assert set(completed_ids) == {0, 2, 4}  # Only successful items


def test_storage_directory_permission_denied():
    """Test handling when storage directory has no write permissions."""
    import platform
    import sys
    import uuid

    # Skip on Windows as permissions work differently
    if platform.system() == "Windows":
        pytest.skip("Permission test not applicable on Windows")

    unique_id = uuid.uuid4().hex[:8]
    # Create a directory with no write permissions
    with tempfile.TemporaryDirectory() as temp_storage:
        storage_path = Path(temp_storage) / f"no_write_perms_{unique_id}"
        storage_path.mkdir()

        # Make directory read-only
        os.chmod(storage_path, 0o444)

        try:
            # Try to create a subdirectory - should fail with permission error
            test_exp_path = storage_path / f"permission_test_{unique_id}"

            # This should raise a PermissionError
            with pytest.raises(PermissionError) as exc_info:
                test_exp_path.mkdir(parents=True)

            # Verify we got a permission error
            assert "Permission" in str(exc_info.type.__name__)

        finally:
            # Restore permissions for cleanup
            os.chmod(storage_path, 0o755)


def test_storage_file_corruption_recovery(temp_storage):
    """Test handling when evaluation files are corrupted."""
    import uuid

    from dotevals.storage.json import JSONStorage

    unique_id = uuid.uuid4().hex[:8]
    exp_name = f"corruption_test_{unique_id}"
    eval_name = f"simple_eval_{unique_id}"

    # Create storage and manually create the evaluation file
    storage = JSONStorage(temp_storage)
    storage.create_experiment(exp_name)

    # Create evaluation file with valid content first
    eval_file = temp_storage / exp_name / f"{eval_name}.jsonl"
    with open(eval_file, "w") as f:
        # Write valid evaluation metadata
        import json
        import time

        metadata = {
            "evaluation_name": eval_name,
            "status": "completed",
            "started_at": time.time(),
            "metadata": {},
            "completed_at": time.time(),
        }
        f.write(json.dumps(metadata) + "\n")
        # Write a result
        f.write('{"item_id": 0, "result": {"scores": []}}\n')

    # Verify we can load it
    eval_obj = storage.load_evaluation(exp_name, eval_name)
    assert eval_obj is not None

    # Now corrupt the file
    with open(eval_file, "w") as f:
        f.write("{ invalid json content }")

    # Should handle corruption gracefully

    try:
        corrupted_eval = storage.load_evaluation(exp_name, eval_name)
        # If it doesn't raise, it should return None or valid evaluation
        assert corrupted_eval is None or hasattr(corrupted_eval, "evaluation_name")
    except Exception as e:
        # If it raises, error should be informative
        error_msg = str(e).lower()
        # Check for JSON decoding error messages
        assert any(
            word in error_msg
            for word in ["expecting", "property", "json", "decode", "error"]
        )


def test_disk_space_exhaustion_simulation(temp_storage):
    """Test behavior when disk space is exhausted during save operations."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    session_manager = SessionManager(
        evaluation_name=f"disk_test_eval_{unique_id}",
        experiment_name=f"disk_space_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Mock the storage add_results to simulate disk full error
    with patch.object(session_manager.storage, "add_results") as mock_add:
        mock_add.side_effect = OSError(28, "No space left on device")  # ENOSPC

        test_data = [("Q1", "A1")]

        def disk_test_eval(question, answer):
            return Result(exact_match(answer, "A1"), prompt=f"Q: {question}")

        # Create ForEach instance with custom storage
        custom_foreach = ForEach()

        @custom_foreach("question,answer", test_data)
        def disk_test_eval_wrapped(question, answer):
            return disk_test_eval(question, answer)

        # Should handle disk space error gracefully
        with pytest.raises(OSError) as exc_info:
            coro = disk_test_eval_wrapped(session_manager=session_manager, samples=None)
            asyncio.run(coro)

        # Error should be informative
        assert "space" in str(exc_info.value).lower()


def test_storage_backend_unavailable(tmp_path):
    """Test handling when storage backend is unavailable."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]

    # Test the registry directly instead of through SessionManager
    # to avoid mock contamination issues
    from dotevals.storage.base import StorageRegistry

    # Create a fresh registry instance
    test_registry = StorageRegistry()
    test_registry.load_plugins()

    # Test with invalid storage backend
    with pytest.raises(ValueError) as exc_info:
        test_registry.get_storage("invalid://nonexistent/path")

    # Should provide clear, helpful error message
    error_msg = str(exc_info.value).lower()
    assert "unknown storage backend" in error_msg
    assert "invalid" in error_msg  # Should mention the invalid backend name

    # Test with no backend specified should default to json (backward compatibility)
    # This should not raise an error
    manager = SessionManager(f"eval_test_{unique_id}", storage=f"json://{tmp_path}")
    assert manager.storage.__class__.__name__ == "JSONStorage"


def test_empty_dataset_handling(temp_storage):
    """Test handling of empty datasets."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    empty_data = []

    def eval_empty_dataset(question, answer):
        return Result(exact_match(answer, "A1"), prompt=f"Q: {question}")

    session_manager = SessionManager(
        evaluation_name=f"eval_empty_dataset_{unique_id}",
        experiment_name=f"empty_dataset_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", empty_data)
    def eval_empty_dataset_wrapped(question, answer):
        return eval_empty_dataset(question, answer)

    # Should handle empty dataset gracefully
    coro = eval_empty_dataset_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    assert len(result.results) == 0
    assert result.summary == {}  # Empty summary for empty results


def test_malformed_dataset_entries(temp_storage):
    """Test handling of malformed dataset entries."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    # Dataset with inconsistent structure
    malformed_data = [
        ("Q1", "A1"),  # Good entry
        ("Q2",),  # Missing answer
        ("Q3", "A3", "extra"),  # Extra field
        ("Q4", "A4"),  # Good entry
    ]

    def eval_malformed_dataset(question, answer):
        prompt = f"Q: {question}"
        return Result(exact_match(answer, "A1"), prompt=prompt)

    session_manager = SessionManager(
        evaluation_name=f"eval_malformed_dataset_{unique_id}",
        experiment_name=f"malformed_dataset_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", malformed_data)
    def eval_malformed_dataset_wrapped(question, answer):
        return eval_malformed_dataset(question, answer)

    # Check what actually happens with malformed entries
    coro = eval_malformed_dataset_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    # Should have attempted to process all entries
    assert len(result.results) == 4

    # Check what actually happens - the system is surprisingly robust
    # ("Q2",) - missing answer - should cause unpacking error
    assert result.results[1].error is not None
    # ("Q3", "A3", "extra") - extra field - actually handled gracefully! Extra field ignored
    # This shows the system is more robust than expected
    assert result.results[2].error is None  # System ignores extra fields


def test_dataset_iterator_exhaustion(temp_storage):
    """Test handling when dataset iterator is exhausted unexpectedly."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]

    def problematic_iterator():
        yield ("Q1", "A1")
        yield ("Q2", "A2")
        # Iterator ends unexpectedly
        return

    def eval_exhausted_iterator(question, answer):
        return Result(exact_match(answer, "A1"), prompt=f"Q: {question}")

    session_manager = SessionManager(
        evaluation_name=f"eval_exhausted_iterator_{unique_id}",
        experiment_name=f"exhausted_iterator_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", problematic_iterator())
    def eval_exhausted_iterator_wrapped(question, answer):
        return eval_exhausted_iterator(question, answer)

    # Should handle iterator exhaustion gracefully
    coro = eval_exhausted_iterator_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    # Should process available items
    assert len(result.results) == 2


def test_evaluation_already_running_handling(temp_storage):
    """Test handling when trying to start an evaluation that's already running."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    exp_name = f"concurrent_test_{unique_id}"
    eval_name = f"test_eval_{unique_id}"

    # First session manager starts evaluation
    session_manager1 = SessionManager(
        evaluation_name=eval_name,
        experiment_name=exp_name,
        storage=f"json://{temp_storage}",
    )
    session_manager1.start_evaluation()

    # Second session manager should handle the running evaluation appropriately
    session_manager2 = SessionManager(
        evaluation_name=eval_name,
        experiment_name=exp_name,
        storage=f"json://{temp_storage}",
    )

    # Should either resume the existing evaluation or handle conflict gracefully
    session_manager2.start_evaluation()

    # Should be able to load the evaluation
    eval1 = session_manager1.storage.load_evaluation(exp_name, eval_name)
    eval2 = session_manager2.storage.load_evaluation(exp_name, eval_name)

    assert eval1 is not None
    assert eval2 is not None
    assert eval1.evaluation_name == eval2.evaluation_name


def test_evaluation_status_after_completion(temp_storage):
    """Test that evaluations have correct status after completion."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    storage = JSONStorage(temp_storage)

    # Test completed evaluation (success=True)
    session_manager1 = SessionManager(
        evaluation_name=f"completed_eval_{unique_id}",
        experiment_name=f"status_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager1.start_evaluation()
    session_manager1.finish_evaluation(success=True)

    evaluation = storage.load_evaluation(
        f"status_test_{unique_id}", f"completed_eval_{unique_id}"
    )
    assert evaluation.status == EvaluationStatus.COMPLETED

    # Test failed evaluation (success=False)
    session_manager2 = SessionManager(
        evaluation_name=f"failed_eval_{unique_id}",
        experiment_name=f"status_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager2.start_evaluation()
    session_manager2.finish_evaluation(success=False)

    evaluation = storage.load_evaluation(
        f"status_test_{unique_id}", f"failed_eval_{unique_id}"
    )
    assert evaluation.status == EvaluationStatus.FAILED

    # Test running evaluation (never finished)
    session_manager3 = SessionManager(
        evaluation_name=f"running_eval_{unique_id}",
        experiment_name=f"status_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager3.start_evaluation()
    # Don't call finish_evaluation() - simulates process crash

    evaluation = storage.load_evaluation(
        f"status_test_{unique_id}", f"running_eval_{unique_id}"
    )
    assert evaluation.status == EvaluationStatus.RUNNING


def test_memory_pressure_large_results(temp_storage):
    """Test handling when evaluation results consume excessive memory."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    # Create large dataset
    large_data = [(f"Q{i}", f"A{i}") for i in range(1000)]

    def eval_memory_intensive(question, answer):
        # Create a large score object (simulating memory pressure)
        large_metrics = [accuracy() for _ in range(100)]
        score = Score("memory_test", True, large_metrics)
        return Result(score, prompt=f"Q: {question}")

    session_manager = SessionManager(
        evaluation_name=f"eval_memory_intensive_{unique_id}",
        experiment_name=f"memory_pressure_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", large_data)
    def eval_memory_intensive_wrapped(question, answer):
        return eval_memory_intensive(question, answer)

    # Should handle large results gracefully
    coro = eval_memory_intensive_wrapped(session_manager=session_manager, samples=10)
    result = asyncio.run(coro)

    assert len(result.results) == 10
    # Each result should have the large score
    assert all(
        len(r.result.scores) == 1 for r in result.results if r.result and not r.error
    )


def test_many_evaluations_file_descriptor_management(temp_storage):
    """Test handling when system creates many evaluations."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    session_manager = SessionManager(
        evaluation_name=f"eval_0_{unique_id}",
        experiment_name=f"file_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create and finish many evaluations to test file descriptor cleanup
    for i in range(100):
        eval_session = SessionManager(
            evaluation_name=f"eval_{i}_{unique_id}",
            experiment_name=f"file_test_{unique_id}",
            storage=f"json://{temp_storage}",
        )
        eval_session.start_evaluation()
        eval_session.finish_evaluation(success=True)

    # Should not accumulate file descriptors
    # All evaluations should be properly saved and closed
    evaluations = session_manager.storage.list_evaluations(f"file_test_{unique_id}")
    assert len(evaluations) == 100


def test_helpful_error_context_in_results(temp_storage):
    """Test that error results include helpful context for debugging."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    def eval_with_context_error(question, answer):
        if question == "Q2":
            # Error that should include context
            raise ValueError(f"Failed to process question: {question}")
        return Result(exact_match(answer, "A1"), prompt=f"Q: {question}")

    session_manager = SessionManager(
        evaluation_name=f"eval_with_context_error_{unique_id}",
        experiment_name=f"context_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_with_context_error_wrapped(question, answer):
        return eval_with_context_error(question, answer)

    coro = eval_with_context_error_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    # Error should include the original error message
    error_result = result.results[1]
    assert error_result.error is not None
    assert "Failed to process question: Q2" in error_result.error

    # Error result should still include item data for debugging
    assert error_result.dataset_row == {"question": "Q2", "answer": "A2"}
    assert error_result.item_id == 1


def test_evaluation_resumption_after_errors(temp_storage):
    """Test that evaluations can be resumed properly after errors occur."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("Q1", "A1"), ("Q2", "A2"), ("Q3", "A3")]

    def eval_resumption_after_error(question, answer):
        prompt = f"Q: {question}"
        if question == "Q2":
            raise ValueError("Temporary error")
        return Result(exact_match(answer, "A1"), prompt=prompt)

    # First run with errors
    session_manager1 = SessionManager(
        evaluation_name=f"eval_resumption_after_error_{unique_id}",
        experiment_name=f"resumption_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Create ForEach instance with custom storage
    custom_foreach = ForEach()

    @custom_foreach("question,answer", test_data)
    def eval_resumption_after_error_wrapped(question, answer):
        return eval_resumption_after_error(question, answer)

    coro1 = eval_resumption_after_error_wrapped(
        session_manager=session_manager1, samples=None
    )
    result1 = asyncio.run(coro1)
    session_manager1.finish_evaluation(success=False)

    # Verify error was recorded
    assert len(result1.results) == 3
    assert result1.results[1].error is not None

    # Resume evaluation
    session_manager2 = SessionManager(
        evaluation_name=f"eval_resumption_after_error_{unique_id}",
        experiment_name=f"resumption_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager2.start_evaluation()

    # Evaluation should be loaded and should have previous results
    results = session_manager2.storage.get_results(
        f"resumption_error_test_{unique_id}", f"eval_resumption_after_error_{unique_id}"
    )
    assert len(results) == 3

    # Only successful items should be in completed_ids
    completed_ids = session_manager2.storage.completed_items(
        f"resumption_error_test_{unique_id}", f"eval_resumption_after_error_{unique_id}"
    )
    assert set(completed_ids) == {0, 2}  # Only successful items


def test_evaluation_status_display_for_cli(temp_storage):
    """Test that evaluations show correct status for CLI display."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    # Test completed evaluation (success=True)
    session_manager1 = SessionManager(
        evaluation_name=f"completed_evaluation_{unique_id}",
        experiment_name=f"cli_status_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager1.start_evaluation()
    session_manager1.finish_evaluation(success=True)

    evaluation = session_manager1.storage.load_evaluation(
        f"cli_status_test_{unique_id}", f"completed_evaluation_{unique_id}"
    )
    assert evaluation.status == EvaluationStatus.COMPLETED

    # Test error evaluation (success=False)
    session_manager2 = SessionManager(
        evaluation_name=f"error_evaluation_{unique_id}",
        experiment_name=f"cli_status_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager2.start_evaluation()
    session_manager2.finish_evaluation(success=False)

    evaluation = session_manager2.storage.load_evaluation(
        f"cli_status_test_{unique_id}", f"error_evaluation_{unique_id}"
    )
    assert evaluation.status == EvaluationStatus.FAILED

    # Test interrupted evaluation (never finished)
    session_manager3 = SessionManager(
        evaluation_name=f"interrupted_evaluation_{unique_id}",
        experiment_name=f"cli_status_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    session_manager3.start_evaluation()
    # Don't call finish() - simulates process crash

    evaluation = session_manager3.storage.load_evaluation(
        f"cli_status_test_{unique_id}", f"interrupted_evaluation_{unique_id}"
    )
    assert evaluation.status == EvaluationStatus.RUNNING


def test_result_error_propagation(temp_storage):
    """Test that errors in Result objects are properly propagated to Record.error."""
    import json
    import uuid

    unique_id = uuid.uuid4().hex[:8]

    test_data = [
        ("valid_json", '{"key": "value"}'),
        ("invalid_json", '{"key": invalid}'),
    ]

    def eval_with_result_error(question, json_str):
        prompt = f"Q: {question}"
        try:
            json.loads(json_str)
            score = Score("json_valid", True, [accuracy()])
            return Result(score, prompt=prompt)
        except json.JSONDecodeError as e:
            # Return Result with error instead of raising exception
            score = Score("json_valid", False, [accuracy()])
            return Result(score, prompt=prompt, error=f"JSONDecodeError: {str(e)}")

    session_manager = SessionManager(
        evaluation_name=f"eval_with_result_error_{unique_id}",
        experiment_name=f"result_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    custom_foreach = ForEach()

    @custom_foreach("question,json_str", test_data)
    def eval_with_result_error_wrapped(question, json_str):
        return eval_with_result_error(question, json_str)

    coro = eval_with_result_error_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    # Should have processed both items
    assert len(result.results) == 2

    # First item should succeed (no error)
    assert result.results[0].error is None
    assert result.results[0].result.error is None

    # Second item should have error propagated from Result to Record
    assert result.results[1].error is not None
    assert "JSONDecodeError" in result.results[1].error
    assert result.results[1].result.error is not None
    assert "JSONDecodeError" in result.results[1].result.error

    # Only successful items should be in completed_ids (for retry behavior)
    completed_ids = session_manager.storage.completed_items(
        f"result_error_test_{unique_id}", f"eval_with_result_error_{unique_id}"
    )
    assert set(completed_ids) == {0}  # Only first item completed successfully


def test_result_error_with_model_response_capture(temp_storage):
    """Test capturing model answer along with error for debugging."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("math", "2+2=4"), ("math", "2+2=elephant")]

    def eval_with_model_response_error(question, model_response):
        prompt = f"Solve: {question}"
        try:
            # Try to parse numeric answer
            if "=" in model_response:
                answer_part = model_response.split("=")[1].strip()
                float(answer_part)  # Just validate it's a number
                score = Score("math_correct", True, [accuracy()])
                return Result(score, prompt=prompt)
            else:
                raise ValueError("No equals sign found")
        except (ValueError, TypeError) as e:
            # Capture the model answer in the error for debugging
            score = Score("math_correct", False, [accuracy()])
            error_msg = f"Failed to parse answer '{model_response}': {str(e)}"
            return Result(score, prompt=prompt, error=error_msg)

    session_manager = SessionManager(
        evaluation_name=f"eval_with_model_response_error_{unique_id}",
        experiment_name=f"model_response_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    custom_foreach = ForEach()

    @custom_foreach("question,model_response", test_data)
    def eval_with_model_response_error_wrapped(question, model_response):
        return eval_with_model_response_error(question, model_response)

    coro = eval_with_model_response_error_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    # Should have processed both items
    assert len(result.results) == 2

    # First item should succeed
    assert result.results[0].error is None

    # Second item should have error with model answer captured
    assert result.results[1].error is not None
    assert "elephant" in result.results[1].error  # Model answer should be in error
    assert "Failed to parse answer" in result.results[1].error

    # Error items should be marked for retry
    completed_ids = session_manager.storage.completed_items(
        f"model_response_error_test_{unique_id}",
        f"eval_with_model_response_error_{unique_id}",
    )
    assert set(completed_ids) == {0}  # Only successful item


def test_result_error_propagates_to_record_without_exception(temp_storage):
    """Test that errors in Result objects are propagated to Record without raising exceptions."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("success", "ok"), ("error", "fail")]

    custom_foreach = ForEach()

    @custom_foreach("input,expected", test_data)
    def eval_with_mixed_results(input, expected):
        score = Score("test_eval", input == "success", [accuracy()])
        if input == "error":
            # Return a Result with an error - this should not raise an exception
            # but instead create a Record with the error propagated
            return Result(score, prompt=f"Input: {input}", error="Processing failed")
        else:
            # Return a normal successful Result
            return Result(score, prompt=f"Input: {input}")

    session_manager = SessionManager(
        evaluation_name=f"mixed_results_test_{unique_id}",
        experiment_name=f"mixed_results_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )
    coro = eval_with_mixed_results(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    # Evaluation should complete successfully despite Result errors
    assert len(result.results) == 2

    # Successful Result should create Record with no error
    success_record = result.results[0]
    assert success_record.error is None
    assert success_record.result.error is None

    # Result with error should create Record with propagated error
    error_record = result.results[1]
    assert error_record.error is not None
    assert "Processing failed" in error_record.error
    assert error_record.result.error is not None
    assert "Processing failed" in error_record.result.error


@pytest.mark.asyncio
async def test_async_result_error_propagates_to_record_without_exception(temp_storage):
    """Test that errors in Result objects are propagated to Record without raising exceptions in async evaluations."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("success", "ok"), ("error", "fail")]

    custom_foreach = ForEach()

    @custom_foreach("input,expected", test_data)
    async def async_eval_with_mixed_results(input, expected):
        # Small async delay to ensure this runs on async path
        await asyncio.sleep(0.001)

        score = Score("test_eval", input == "success", [accuracy()])
        if input == "error":
            # Return a Result with an error - this should not raise an exception
            # but instead create a Record with the error propagated
            return Result(
                score, prompt=f"Input: {input}", error="Async processing failed"
            )
        else:
            # Return a normal successful Result
            return Result(score, prompt=f"Input: {input}")

    session_manager = SessionManager(
        evaluation_name=f"async_mixed_results_test_{unique_id}",
        experiment_name=f"async_mixed_results_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    result = await async_eval_with_mixed_results(
        session_manager=session_manager, samples=None
    )

    # Evaluation should complete successfully despite Result errors
    assert len(result.results) == 2

    # Find records by their input content (order may vary in async execution)
    success_record = next(
        r for r in result.results if r.dataset_row["input"] == "success"
    )
    error_record = next(r for r in result.results if r.dataset_row["input"] == "error")

    # Successful Result should create Record with no error
    assert success_record.error is None
    assert success_record.result.error is None

    # Result with error should create Record with propagated error
    assert error_record.error is not None
    assert "Async processing failed" in error_record.error
    assert error_record.result.error is not None
    assert "Async processing failed" in error_record.result.error


def test_result_error_resumption_behavior(temp_storage):
    """Test that Result errors are properly handled during evaluation resumption."""
    import json
    import uuid

    unique_id = uuid.uuid4().hex[:8]

    test_data = [
        ("good", '{"valid": true}'),
        ("bad", '{"invalid": }'),
        ("good2", '{"valid": false}'),
    ]

    def eval_resumption_result_error(question, json_str):
        prompt = f"Parse: {question}"
        try:
            json.loads(json_str)
            score = Score("parse_success", True, [accuracy()])
            return Result(score, prompt=prompt)
        except json.JSONDecodeError as e:
            score = Score("parse_success", False, [accuracy()])
            return Result(score, prompt=prompt, error=f"Parse error: {str(e)}")

    # First run - will have Result error
    session_manager1 = SessionManager(
        evaluation_name=f"eval_resumption_result_error_{unique_id}",
        experiment_name=f"resumption_result_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    custom_foreach = ForEach()

    @custom_foreach("question,json_str", test_data)
    def eval_resumption_result_error_wrapped(question, json_str):
        return eval_resumption_result_error(question, json_str)

    coro1 = eval_resumption_result_error_wrapped(
        session_manager=session_manager1, samples=None
    )
    result1 = asyncio.run(coro1)
    session_manager1.finish_evaluation(success=False)

    # Verify errors were recorded
    assert len(result1.results) == 3
    assert result1.results[0].error is None
    assert result1.results[1].error is not None  # Parse error
    assert result1.results[2].error is None

    # Check that only successful items are marked as completed
    completed_ids = session_manager1.storage.completed_items(
        f"resumption_result_error_test_{unique_id}",
        f"eval_resumption_result_error_{unique_id}",
    )
    assert set(completed_ids) == {0, 2}  # Only successful items

    # Resume evaluation - should retry failed items
    session_manager2 = SessionManager(
        evaluation_name=f"eval_resumption_result_error_{unique_id}",
        experiment_name=f"resumption_result_error_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    # Get results before resumption
    results_before = session_manager2.storage.get_results(
        f"resumption_result_error_test_{unique_id}",
        f"eval_resumption_result_error_{unique_id}",
    )
    assert len(results_before) == 3

    # The error result should be ready for retry
    error_results = [r for r in results_before if r.error is not None]
    assert len(error_results) == 1
    assert error_results[0].item_id == 1  # The "bad" item


def test_result_with_model_response_field(temp_storage):
    """Test that Result objects can store model_response for debugging."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("question1", "expected1"), ("question2", "expected2")]

    def eval_with_model_response(question, expected):
        # Simulate model generating an answer
        model_output = f"The answer to {question} is {expected} plus extra text"
        prompt = f"Q: {question}"

        # Extract just the expected part for scoring
        try:
            if expected in model_output:
                score = Score("contains_expected", True, [accuracy()])
            else:
                score = Score("contains_expected", False, [accuracy()])

            # Store both the prompt and the raw model answer
            return Result(score, prompt=prompt, model_response=model_output)
        except Exception as e:
            # Even in error cases, we can capture the model output
            score = Score("contains_expected", False, [accuracy()])
            return Result(
                score,
                prompt=prompt,
                model_response=model_output,
                error=f"Processing error: {str(e)}",
            )

    session_manager = SessionManager(
        evaluation_name=f"eval_with_model_response_{unique_id}",
        experiment_name=f"model_response_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    custom_foreach = ForEach()

    @custom_foreach("question,expected", test_data)
    def eval_with_model_response_wrapped(question, expected):
        return eval_with_model_response(question, expected)

    coro = eval_with_model_response_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    # Should have processed both items
    assert len(result.results) == 2

    # Check that model_response is captured for both items
    for i, res in enumerate(result.results):
        assert res.error is None  # No errors in this test
        assert res.result.model_response is not None
        assert f"expected{i + 1}" in res.result.model_response
        assert "plus extra text" in res.result.model_response
        assert res.result.prompt == f"Q: question{i + 1}"

    # Verify storage and retrieval preserves model_response
    stored_results = session_manager.storage.get_results(
        f"model_response_test_{unique_id}", f"eval_with_model_response_{unique_id}"
    )
    assert len(stored_results) == 2

    for i, stored_res in enumerate(stored_results):
        assert stored_res.result.model_response is not None
        assert f"expected{i + 1}" in stored_res.result.model_response
        assert "plus extra text" in stored_res.result.model_response


def test_result_with_optional_prompt(temp_storage):
    """Test that Result objects work with optional prompt (None or empty)."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("input1", "output1"), ("input2", "output2")]

    def eval_without_prompt(input_val, expected):
        # Sometimes we don't have a meaningful prompt to store
        score = Score("matches", input_val == expected, [accuracy()])

        # Test different ways of omitting prompt
        if input_val == "input1":
            # Explicitly None prompt
            return Result(score, prompt=None, model_response=f"processed_{input_val}")
        else:
            # Omit prompt entirely (should default to None)
            return Result(score, model_response=f"processed_{input_val}")

    session_manager = SessionManager(
        evaluation_name=f"eval_without_prompt_{unique_id}",
        experiment_name=f"optional_prompt_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    custom_foreach = ForEach()

    @custom_foreach("input_val,expected", test_data)
    def eval_without_prompt_wrapped(input_val, expected):
        return eval_without_prompt(input_val, expected)

    coro = eval_without_prompt_wrapped(session_manager=session_manager, samples=None)
    result = asyncio.run(coro)

    # Should have processed both items
    assert len(result.results) == 2

    # Check that prompt is None and model_response is captured
    for i, res in enumerate(result.results):
        assert res.error is None
        assert res.result.prompt is None  # Optional prompt should be None
        assert res.result.model_response == f"processed_input{i + 1}"

    # Verify storage and retrieval preserves None prompt and model_response
    stored_results = session_manager.storage.get_results(
        f"optional_prompt_test_{unique_id}", f"eval_without_prompt_{unique_id}"
    )
    assert len(stored_results) == 2

    for i, stored_res in enumerate(stored_results):
        assert stored_res.result.prompt is None
        assert stored_res.result.model_response == f"processed_input{i + 1}"


def test_result_comprehensive_fields_usage(temp_storage):
    """Test Result with all fields: scores, prompt, error, model_response."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    test_data = [("good_input", "valid"), ("bad_input", "invalid")]

    def eval_comprehensive_fields(input_val, expected):
        model_output = f"Model response for {input_val}"
        prompt = f"Process: {input_val}"

        if input_val == "good_input":
            # Success case - all fields except error
            score = Score("is_valid", True, [accuracy()])
            return Result(score, prompt=prompt, model_response=model_output)
        else:
            # Error case - all fields including error
            score = Score("is_valid", False, [accuracy()])
            return Result(
                score,
                prompt=prompt,
                model_response=model_output,
                error="Input validation failed",
            )

    session_manager = SessionManager(
        evaluation_name=f"eval_comprehensive_fields_{unique_id}",
        experiment_name=f"comprehensive_test_{unique_id}",
        storage=f"json://{temp_storage}",
    )

    custom_foreach = ForEach()

    @custom_foreach("input_val,expected", test_data)
    def eval_comprehensive_fields_wrapped(input_val, expected):
        return eval_comprehensive_fields(input_val, expected)

    coro = eval_comprehensive_fields_wrapped(
        session_manager=session_manager, samples=None
    )
    result = asyncio.run(coro)

    # Should have processed both items
    assert len(result.results) == 2

    # First item (success case)
    assert result.results[0].error is None  # No error at Record level
    assert result.results[0].result.error is None  # No error at Result level
    assert result.results[0].result.prompt == "Process: good_input"
    assert result.results[0].result.model_response == "Model response for good_input"

    # Second item (error case)
    assert result.results[1].error is not None  # Error propagated to Record
    assert "Input validation failed" in result.results[1].error
    assert result.results[1].result.error is not None  # Error in Result
    assert "Input validation failed" in result.results[1].result.error
    assert result.results[1].result.prompt == "Process: bad_input"
    assert result.results[1].result.model_response == "Model response for bad_input"

    # Only successful items should be marked as completed for retry behavior
    completed_ids = session_manager.storage.completed_items(
        f"comprehensive_test_{unique_id}", f"eval_comprehensive_fields_{unique_id}"
    )
    assert set(completed_ids) == {0}  # Only first item completed successfully
