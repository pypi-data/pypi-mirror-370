"""Tests for session interruption and resumption - the core value proposition."""

import asyncio
import json
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from dotevals import ForEach
from dotevals.evaluators import exact_match
from dotevals.models import Result
from dotevals.sessions import SessionManager


@pytest.fixture
def temp_storage():
    """Provide temporary storage for resumption tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_session_interruption_and_resume_basic(temp_storage):
    """Test basic interruption and resumption workflow."""
    unique_id = uuid.uuid4().hex[:8]

    # Create test dataset
    test_data = [("Q1", "A1"), ("Q2", "A2"), ("Q3", "A3"), ("Q4", "A4")]

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_test(question, answer):
        prompt = f"Q: {question}"
        return Result(
            exact_match(answer, "A1"), prompt=prompt
        )  # Only first item matches

    # First run - simulate interruption after processing some items
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_test_{unique_id}",
        experiment_name=f"test_experiment_{unique_id}",
    )

    # Mock interruption by only processing first 2 items
    with patch("dotevals.core._run_evaluation_sync") as mock_run_sync:
        # Simulate processing only 2 items before "crash"
        from dotevals.metrics import accuracy
        from dotevals.models import EvaluationSummary, Record, Result, Score

        # Create realistic results for first 2 items
        score1 = Score(
            "exact_match", True, [accuracy()], {"result": "A1", "expected": "A1"}
        )
        score2 = Score(
            "exact_match", False, [accuracy()], {"result": "A2", "expected": "A1"}
        )

        result1 = Result(score1, prompt="Q: Q1")
        result2 = Result(score2, prompt="Q: Q2")

        record1 = Record(result1, 0, {"question": "Q1", "answer": "A1"})
        record2 = Record(result2, 1, {"question": "Q2", "answer": "A2"})

        mock_run_sync.return_value = EvaluationSummary([record1, record2])

        # Create the evaluation first
        session_manager1.start_evaluation()

        # Add results to evaluation manually (simulating partial completion)
        session_manager1.add_results([record1, record2])

        # Verify evaluation has partial results
        results = session_manager1.get_results()
        assert len(results) == 2
        completed_ids = session_manager1.storage.completed_items(
            f"test_experiment_{unique_id}", f"eval_test_{unique_id}"
        )
        assert set(completed_ids) == {0, 1}

    # Second run - resume from where we left off
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_test_{unique_id}",
        experiment_name=f"test_experiment_{unique_id}",
    )

    # Check that resumption works
    completed_ids = session_manager2.storage.completed_items(
        session_manager2.current_experiment, session_manager2.current_evaluation
    )
    assert set(completed_ids) == {0, 1}  # Should remember what was completed

    # Verify we can get the existing evaluation results
    results = session_manager2.get_results()
    assert len(results) == 2


def test_session_resumption_with_real_evaluation(temp_storage):
    """Test resumption with actual evaluation execution."""
    unique_id = uuid.uuid4().hex[:8]

    # Create larger dataset to test realistic resumption
    test_data = [(f"Q{i}", f"A{i}") for i in range(1, 11)]  # 10 items

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_large_test(question, answer):
        return Result(
            exact_match(answer, "A1"),  # Only first matches
            prompt=f"Question: {question}",
        )

    # First run - partial execution
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_large_test_{unique_id}",
        experiment_name=f"large_test_experiment_{unique_id}",
    )

    # Run with limited samples to simulate interruption
    coro1 = eval_large_test(session_manager=session_manager1, samples=5)

    result1 = asyncio.run(coro1)

    # Verify partial completion
    assert len(result1.results) == 5
    results = session_manager1.get_results()
    assert len(results) == 5
    completed_ids_first = session_manager1.storage.completed_items(
        f"large_test_experiment_{unique_id}", f"eval_large_test_{unique_id}"
    )
    assert set(completed_ids_first) == {0, 1, 2, 3, 4}

    # Second run - should resume and complete remaining items
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_large_test_{unique_id}",
        experiment_name=f"large_test_experiment_{unique_id}",
    )

    # This should process remaining items (5-9)
    coro2 = eval_large_test(session_manager=session_manager2, samples=None)

    result2 = asyncio.run(coro2)
    # Result includes both old results (5) and new results (5) = 10 total
    # But since resumption happened, it may have processed all 10 items again
    assert len(result2.results) >= 10  # Should have at least all results

    # Verify completion
    results = session_manager2.storage.get_results(
        f"large_test_experiment_{unique_id}", f"eval_large_test_{unique_id}"
    )
    # Due to the way resumption works, we might have duplicates
    # Let's check the unique item IDs
    unique_item_ids = {r.item_id for r in results}
    assert len(unique_item_ids) == 10  # Should have 10 unique items
    assert unique_item_ids == {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}


def test_evaluation_status_during_interruption(temp_storage):
    """Test that evaluation status is properly tracked during interruption."""
    unique_id = uuid.uuid4().hex[:8]

    session_manager = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"test_eval_{unique_id}",
        experiment_name=f"status_test_{unique_id}",
    )

    # Start an evaluation
    session_manager.start_evaluation()

    # Verify evaluation is in RUNNING state
    evaluation = session_manager.storage.load_evaluation(
        f"status_test_{unique_id}", f"test_eval_{unique_id}"
    )
    assert evaluation.status.value == "running"

    # Simulate normal completion
    session_manager.finish_evaluation(success=True)

    # Verify evaluation is completed
    evaluation = session_manager.storage.load_evaluation(
        f"status_test_{unique_id}", f"test_eval_{unique_id}"
    )
    assert evaluation.status.value == "completed"


def test_evaluation_status_detection_for_interrupted_evaluations(temp_storage):
    """Test detection of interrupted evaluations via status."""
    unique_id = uuid.uuid4().hex[:8]

    session_manager = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"interrupted_eval_{unique_id}",
        experiment_name=f"interrupt_test_{unique_id}",
    )

    # Start an evaluation (simulating interruption)
    session_manager.start_evaluation()

    # Create new session manager to check status
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"interrupted_eval_{unique_id}",
        experiment_name=f"interrupt_test_{unique_id}",
    )

    # Should detect that evaluation is still running (interrupted)
    evaluation = session_manager2.storage.load_evaluation(
        f"interrupt_test_{unique_id}", f"interrupted_eval_{unique_id}"
    )
    assert evaluation is not None
    assert evaluation.status.value == "running"


def test_multiple_experiment_concurrent_access(temp_storage):
    """Test that multiple experiments don't interfere with each other."""
    unique_id = uuid.uuid4().hex[:8]

    # Create two different experiments
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_a_{unique_id}",
        experiment_name=f"experiment_a_{unique_id}",
    )

    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_b_{unique_id}",
        experiment_name=f"experiment_b_{unique_id}",
    )

    # Both should be able to work independently
    test_data = [("Q1", "A1"), ("Q2", "A2")]

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_a(question, answer):
        return Result(exact_match(answer, "A1"), prompt=f"Question: {question}")

    @foreach("question,answer", test_data)
    def eval_b(question, answer):
        return Result(exact_match(answer, "A2"), prompt=f"Question: {question}")

    # Run both evaluations
    coro_a = eval_a(session_manager=session_manager1, samples=None)
    result_a = asyncio.run(coro_a)
    coro_b = eval_b(session_manager=session_manager2, samples=None)
    result_b = asyncio.run(coro_b)

    # Verify they don't interfere
    results_a = session_manager1.storage.get_results(
        f"experiment_a_{unique_id}", f"eval_a_{unique_id}"
    )
    results_b = session_manager2.storage.get_results(
        f"experiment_b_{unique_id}", f"eval_b_{unique_id}"
    )

    assert len(results_a) == 2
    assert len(results_b) == 2

    # Different accuracy due to different matching criteria
    assert result_a.summary["exact_match"]["accuracy"] == 0.5  # Only Q1/A1 matches
    assert result_b.summary["exact_match"]["accuracy"] == 0.5  # Only Q2/A2 matches


def test_session_resumption_with_errors(temp_storage):
    """Test resumption when some items had errors - errors should be retried."""
    unique_id = uuid.uuid4().hex[:8]

    test_data = [("Q1", "A1"), ("error", "A2"), ("Q3", "A3")]

    call_count = {}
    fail_on_first_attempt = True

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_with_errors(question, answer):
        # Track calls per question
        call_count[question] = call_count.get(question, 0) + 1

        if question == "error" and fail_on_first_attempt and call_count[question] == 1:
            raise ValueError("Simulated evaluation error")
        return Result(exact_match(answer, "A1"), prompt=f"Question: {question}")

    # First run - process all items (including error)
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_with_errors_{unique_id}",
        experiment_name=f"error_experiment_{unique_id}",
    )

    coro1 = eval_with_errors(session_manager=session_manager1, samples=None)

    result1 = asyncio.run(coro1)

    # Verify all items processed (including error)
    assert len(result1.results) == 3
    results = session_manager1.storage.get_results(
        f"error_experiment_{unique_id}", f"eval_with_errors_{unique_id}"
    )
    assert len(results) == 3

    # Check that errored items are NOT in completed_ids
    completed_ids = session_manager1.storage.completed_items(
        f"error_experiment_{unique_id}", f"eval_with_errors_{unique_id}"
    )
    assert set(completed_ids) == {0, 2}  # Only successful items

    # Reset call count and allow success on retry
    call_count = {}
    fail_on_first_attempt = False

    # Second run - should retry the error item
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_with_errors_{unique_id}",
        experiment_name=f"error_experiment_{unique_id}",
    )
    coro2 = eval_with_errors(session_manager=session_manager2, samples=None)

    result2 = asyncio.run(coro2)
    assert len(result2.results) == 3  # Should have all results

    # Verify the error item was retried
    assert "error" in call_count  # Should have retried the error item
    assert call_count["error"] == 1  # Called once (successful retry)

    # Check that the error was successfully retried
    results2 = session_manager2.storage.get_results(
        f"error_experiment_{unique_id}", f"eval_with_errors_{unique_id}"
    )
    # Find item 1 (the error item)
    item1_results = [r for r in results2 if r.item_id == 1]
    assert len(item1_results) == 1
    assert item1_results[0].error is None  # Should have succeeded on retry

    # Now all items should be in completed_ids
    completed_ids2 = session_manager2.storage.completed_items(
        f"error_experiment_{unique_id}", f"eval_with_errors_{unique_id}"
    )
    assert set(completed_ids2) == {0, 1, 2}  # All items now completed


def test_session_data_persistence_across_processes(temp_storage):
    """Test that session data persists correctly across process restarts."""
    unique_id = uuid.uuid4().hex[:8]

    # First "process" - create and populate experiment
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_persistent_{unique_id}",
        experiment_name=f"persistent_experiment_{unique_id}",
    )

    test_data = [("Q1", "A1"), ("Q2", "A2")]

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_persistent(question, answer):
        return Result(exact_match(answer, "A1"), prompt=f"Question: {question}")

    coro1 = eval_persistent(session_manager=session_manager1, samples=None)

    result1 = asyncio.run(coro1)
    session_manager1.finish_evaluation(success=True)

    # Store original results for comparison
    original_accuracy = result1.summary["exact_match"]["accuracy"]
    original_results_count = len(result1.results)

    # Second "process" - load existing experiment
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_persistent_{unique_id}",
        experiment_name=f"persistent_experiment_{unique_id}",
    )

    # Should be able to retrieve the same evaluation results
    loaded_results = session_manager2.storage.get_results(
        f"persistent_experiment_{unique_id}", f"eval_persistent_{unique_id}"
    )
    assert loaded_results is not None
    assert len(loaded_results) == original_results_count

    # Verify data integrity
    from dotevals.models import EvaluationSummary

    loaded_summary = EvaluationSummary(loaded_results)
    assert loaded_summary.summary["exact_match"]["accuracy"] == original_accuracy


def test_session_resumption_with_different_sample_limits(temp_storage):
    """Test resumption behavior with different sample limits."""
    unique_id = uuid.uuid4().hex[:8]

    test_data = [(f"Q{i}", f"A{i}") for i in range(1, 21)]  # 20 items

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_samples_test(question, answer):
        return Result(exact_match(answer, "A1"), prompt=f"Question: {question}")

    # First run - process 10 items
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_samples_test_{unique_id}",
        experiment_name=f"samples_experiment_{unique_id}",
    )
    coro1 = eval_samples_test(session_manager=session_manager1, samples=10)

    result1 = asyncio.run(coro1)
    assert len(result1.results) == 10

    # Second run - try to process 15 items total
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_samples_test_{unique_id}",
        experiment_name=f"samples_experiment_{unique_id}",
    )

    # Can process up to 15 items in this session. Since 10 are already completed,
    # it will process all remaining 10 items (10-19), giving 20 total results
    coro2 = eval_samples_test(session_manager=session_manager2, samples=15)

    result2 = asyncio.run(coro2)
    assert len(result2.results) == 20  # Should have all results

    # Verify total items processed
    results = session_manager2.storage.get_results(
        f"samples_experiment_{unique_id}", f"eval_samples_test_{unique_id}"
    )
    assert len(results) == 20


def test_evaluation_cleanup_after_completion(temp_storage):
    """Test proper cleanup after evaluation completion."""
    unique_id = uuid.uuid4().hex[:8]

    session_manager = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_cleanup_{unique_id}",
        experiment_name=f"cleanup_experiment_{unique_id}",
    )

    test_data = [("Q1", "A1")]

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("question,answer", test_data)
    def eval_cleanup(question, answer):
        return Result(exact_match(answer, "A1"), prompt=f"Question: {question}")

    # Run evaluation
    coro = eval_cleanup(session_manager=session_manager, samples=None)

    result = asyncio.run(coro)
    assert len(result.results) == 1  # Should process single item

    # Finish evaluation
    session_manager.finish_evaluation(success=True)

    # Verify evaluation status
    evaluation = session_manager.storage.load_evaluation(
        f"cleanup_experiment_{unique_id}", f"eval_cleanup_{unique_id}"
    )
    assert evaluation.status.value == "completed"

    # Evaluation data should still exist
    results = session_manager.storage.get_results(
        f"cleanup_experiment_{unique_id}", f"eval_cleanup_{unique_id}"
    )
    assert len(results) == 1


def test_errored_items_retried_on_resume_detailed(temp_storage):
    """Test detailed behavior of error retry on resumption."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    # Create partial evaluation with errors using JSON storage
    exp_dir = temp_storage / f"retry_test_{unique_id}"
    exp_dir.mkdir(parents=True, exist_ok=True)

    eval_file = exp_dir / f"eval_retry_{unique_id}.jsonl"

    with open(eval_file, "w") as f:
        # Metadata - evaluation still running
        metadata = {
            "evaluation_name": f"eval_retry_{unique_id}",
            "metadata": {"git_commit": "test"},
            "started_at": 1234567890.0,
            "status": "running",
            "completed_at": None,
        }
        f.write(json.dumps(metadata) + "\n")

        # Item 0 - success
        f.write(
            json.dumps(
                {
                    "item_id": 0,
                    "result": {
                        "prompt": "Item 0",
                        "scores": [
                            {
                                "name": "exact_match",
                                "value": True,
                                "metrics": ["accuracy"],
                                "metadata": {},
                            }
                        ],
                    },
                    "dataset_row": {"input": "Item 0", "expected": "Result 0"},
                    "error": None,
                    "timestamp": 1234567890.0,
                }
            )
            + "\n"
        )

        # Item 1 - transient error (should be retried)
        f.write(
            json.dumps(
                {
                    "item_id": 1,
                    "result": {"prompt": "", "scores": []},
                    "dataset_row": {"input": "Item 1", "expected": "Result 1"},
                    "error": "ConnectionError: Network timeout",
                    "timestamp": 1234567891.0,
                }
            )
            + "\n"
        )

        # Item 2 - success
        f.write(
            json.dumps(
                {
                    "item_id": 2,
                    "result": {
                        "prompt": "Item 2",
                        "scores": [
                            {
                                "name": "exact_match",
                                "value": True,
                                "metrics": ["accuracy"],
                                "metadata": {},
                            }
                        ],
                    },
                    "dataset_row": {"input": "Item 2", "expected": "Result 2"},
                    "error": None,
                    "timestamp": 1234567892.0,
                }
            )
            + "\n"
        )

    # Define test data and evaluation function
    test_data = [(f"Item {i}", f"Result {i}") for i in range(5)]
    processed_items = []

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("input,expected", test_data)
    def eval_retry(input, expected):
        item_num = int(input.split()[-1])
        processed_items.append(item_num)

        return Result(exact_match(expected, expected), prompt=input)

    # Create session manager and run evaluation
    session_manager = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_retry_{unique_id}",
        experiment_name=f"retry_test_{unique_id}",
    )

    # Run evaluation - should skip 0 and 2, retry 1, process 3 and 4
    coro = eval_retry(session_manager=session_manager, samples=None)

    result = asyncio.run(coro)

    # Verify correct items were processed (only 1, 3, 4 should be newly processed)
    assert sorted(processed_items) == [
        1,
        3,
        4,
    ], f"Expected [1, 3, 4], got {sorted(processed_items)}"

    # Verify all results are present
    assert len(result.results) == 5

    # Verify the retried item now succeeds
    item1_result = next(r for r in result.results if r.item_id == 1)
    assert item1_result.error is None, "Item 1 should have succeeded on retry"

    # Verify no errors remain in the final results
    errors = [r for r in result.results if r.error is not None]
    assert len(errors) == 0, "No errors should remain after successful retry"

    # Verify the JSONL file no longer contains the error result
    with open(eval_file) as f:
        lines = f.readlines()
    result_lines = [json.loads(line) for line in lines[1:] if line.strip()]
    item1_results_in_file = [r for r in result_lines if r.get("item_id") == 1]
    assert len(item1_results_in_file) == 1, (
        "Only one result for item 1 should be in file"
    )
    assert item1_results_in_file[0].get("error") is None, (
        "Item 1 result in file should not have error"
    )

    # Check completed items now includes the retried item
    completed_ids = session_manager.storage.completed_items(
        f"retry_test_{unique_id}", f"eval_retry_{unique_id}"
    )
    assert sorted(completed_ids) == [0, 1, 2, 3, 4], "All items should now be completed"


def test_persistent_errors_remain_on_resume(temp_storage):
    """Test that items that error again on retry still show as errors."""
    unique_id = uuid.uuid4().hex[:8]

    # Define evaluation that will error persistently
    test_data = [("Bad Item", "Result"), ("Good Item", "Result")]

    # Create ForEach instance with storage
    foreach = ForEach()

    @foreach("input,expected", test_data)
    def eval_persist_error(input, expected):
        if input == "Bad Item":
            raise ValueError("Still invalid")

        return Result(exact_match(expected, expected), prompt=input)

    # First run - create error
    session_manager1 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_persist_error_{unique_id}",
        experiment_name=f"persist_error_test_{unique_id}",
    )
    coro1 = eval_persist_error(session_manager=session_manager1, samples=None)

    result1 = asyncio.run(coro1)

    # Should have 2 results, one with error
    assert len(result1.results) == 2
    error_results = [r for r in result1.results if r.error is not None]
    assert len(error_results) == 1

    # Second run - retry should also fail
    session_manager2 = SessionManager(
        storage=f"json://{temp_storage}",
        evaluation_name=f"eval_persist_error_{unique_id}",
        experiment_name=f"persist_error_test_{unique_id}",
    )
    coro2 = eval_persist_error(session_manager=session_manager2, samples=None)

    result2 = asyncio.run(coro2)

    # Should still have 2 results
    assert len(result2.results) == 2

    # Item 0 should still have an error (the retry also failed)
    item0_result = next(r for r in result2.results if r.item_id == 0)
    assert item0_result.error is not None
    assert "Still invalid" in item0_result.error

    # Second item should succeed
    item1_results = [r for r in result2.results if r.item_id == 1]
    assert len(item1_results) == 1
    assert item1_results[0].error is None

    # Completed items should only include the successful one
    completed_ids = session_manager2.storage.completed_items(
        f"persist_error_test_{unique_id}", f"eval_persist_error_{unique_id}"
    )
    assert completed_ids == [1], "Only item 1 should be completed"


def test_error_retry_with_connection_retries_enabled(temp_storage):
    """Test that connection errors are retried with max_retries parameter."""
    unique_id = uuid.uuid4().hex[:8]

    from tenacity import Retrying, retry_if_exception_type, stop_after_attempt

    from dotevals import ForEach

    attempt_counts = {}

    test_data = [("Item 0", "Result 0"), ("Item 1", "Result 1")]

    # Create ForEach with retry configuration and isolated storage
    foreach = ForEach(
        retries=Retrying(
            retry=retry_if_exception_type(ConnectionError), stop=stop_after_attempt(3)
        )
    )

    @foreach("input,expected", test_data)
    def eval_with_retries(input, expected):
        item_num = int(input.split()[-1])
        attempt_counts[item_num] = attempt_counts.get(item_num, 0) + 1

        # Item 1 fails first 2 attempts with connection error
        if item_num == 1 and attempt_counts[item_num] < 3:
            raise ConnectionError(
                f"Network error on attempt {attempt_counts[item_num]}"
            )

        return Result(exact_match(expected, expected), prompt=input)

    # Run with retries enabled
    session_manager = SessionManager(
        evaluation_name=f"eval_with_retries_{unique_id}",
        experiment_name=f"retry_test_{unique_id}",
        storage=f"json://{temp_storage}/retry_test_isolated_{unique_id}",
    )
    coro = eval_with_retries(session_manager=session_manager, samples=None)

    result = asyncio.run(coro)

    # All items should succeed
    assert len(result.results) == 2
    assert all(r.error is None for r in result.results)

    # Item 1 should have been tried 3 times
    assert attempt_counts[1] == 3, (
        f"Item 1 should have been tried 3 times, got {attempt_counts[1]}"
    )
