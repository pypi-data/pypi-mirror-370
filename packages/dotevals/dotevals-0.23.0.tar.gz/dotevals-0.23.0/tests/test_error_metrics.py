"""Tests for error handling in metric calculations."""

import asyncio
import tempfile

from dotevals.core import foreach
from dotevals.evaluators import exact_match
from dotevals.models import EvaluationSummary, Record, Result
from dotevals.sessions import SessionManager


def test_errors_included_in_metrics():
    """Test that errors are counted as False in metrics."""
    dataset = [
        ("test1", "answer1"),
        ("test2", "answer2"),
        ("test3", "answer3"),
        ("test4", "answer4"),
    ]

    @foreach("question,answer", dataset)
    def eval_with_errors(question, answer):
        if question == "test2":
            raise ValueError("Simulated error")
        if question == "test4":
            raise RuntimeError("Another error")
        return Result(exact_match(answer, "answer1"), prompt=question)

    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="error_metrics_test",
            evaluation_name="test_eval",
        )
        coro = eval_with_errors(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        # We should have 4 results (2 successful, 2 errors)
        assert len(result.results) == 4

        # Check that errors are included in metric calculation
        # Only test1 matches "answer1", test3 doesn't match, test2 and test4 are errors
        # So accuracy should be 1/4 = 0.25
        assert result.summary["exact_match"]["accuracy"] == 0.25

        # Verify error results exist
        error_results = [r for r in result.results if r.error is not None]
        assert len(error_results) == 2


def test_all_errors_zero_accuracy():
    """Test that all errors result in zero accuracy."""
    dataset = [("test1", "answer1"), ("test2", "answer2")]

    @foreach("question,answer", dataset)
    def eval_all_errors(question, answer):
        raise Exception("Always fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="all_errors_test",
            evaluation_name="test_eval",
        )
        coro = eval_all_errors(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        # All items should have errors
        assert len(result.results) == 2
        assert all(r.error is not None for r in result.results)
        # When all results are errors, there's no score structure to infer
        # So the summary will be empty
        assert result.summary == {}


def test_no_errors_normal_accuracy():
    """Test that no errors results in normal accuracy calculation."""
    dataset = [
        ("test1", "answer1"),
        ("test2", "answer2"),
        ("test3", "answer3"),
    ]

    @foreach("question,answer", dataset)
    def eval_no_errors(question, answer):
        # Match only answer2
        return Result(exact_match(answer, "answer2"), prompt=question)

    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="no_errors_test",
            evaluation_name="test_eval",
        )
        coro = eval_no_errors(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        # No errors, normal calculation
        assert len(result.results) == 3
        assert all(r.error is None for r in result.results)
        # Only test2 matches "answer2"
        assert result.summary["exact_match"]["accuracy"] == 1 / 3


def test_summary_includes_both_metrics():
    """Test that summary includes metrics with and without errors."""
    # Create mock results
    results = [
        Record(
            result=Result(exact_match("a", "a"), prompt="test1"),  # True
            item_id=0,
            dataset_row={"q": "test1"},
            error=None,
        ),
        Record(
            result=Result(exact_match("b", "a"), prompt="test2"),  # False
            item_id=1,
            dataset_row={"q": "test2"},
            error=None,
        ),
        Record(
            result=Result(prompt=""),  # Error - will be changed to False
            item_id=2,
            dataset_row={"q": "test3"},
            error="ConnectionError",
        ),
        Record(
            result=Result(exact_match("a", "a"), prompt="test4"),  # True
            item_id=3,
            dataset_row={"q": "test4"},
            error=None,
        ),
    ]

    # Create summary
    summary = EvaluationSummary(results)
    summary_dict = summary.compute_summary()

    # With errors included as False:
    # 2 True results out of 4 total = 0.5
    assert "exact_match" in summary_dict
    assert summary_dict["exact_match"]["accuracy"] == 0.5


def test_mixed_errors_and_successes():
    """Test evaluation with mix of errors and successful evaluations."""
    dataset = [
        ("q1", "a1"),
        ("q2", "a2"),
        ("q3", "a3"),
        ("q4", "a4"),
        ("q5", "a5"),
    ]

    error_questions = {"q2", "q4"}

    @foreach("question,answer", dataset)
    def eval_mixed(question, answer):
        if question in error_questions:
            raise Exception(f"Error on {question}")
        # Only q1 and q5 match their answers
        return Result(exact_match(question, question), prompt=question)

    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="mixed_test",
            evaluation_name="test_eval",
        )
        coro = eval_mixed(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        # All 5 items should be in results
        assert len(result.results) == 5

        # Count errors
        error_count = sum(1 for r in result.results if r.error is not None)
        assert error_count == 2

        # With errors counted as False:
        # q1: True, q2: False (error), q3: True, q4: False (error), q5: True
        # Accuracy should be 3/5 = 0.6
        assert result.summary["exact_match"]["accuracy"] == 0.6


def test_error_preserves_dataset_row():
    """Test that error results preserve dataset row information."""
    dataset = [("question_text", "answer_text", "extra_info")]

    @foreach("q,a,info", dataset)
    def eval_preserve_row(q, a, info):
        raise ValueError("Test error")

    with tempfile.TemporaryDirectory() as temp_dir:
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="preserve_row_test",
            evaluation_name="test_eval",
        )
        coro = eval_preserve_row(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        assert len(result.results) == 1
        error_result = result.results[0]

        # Dataset row should be preserved
        assert error_result.dataset_row == {
            "q": "question_text",
            "a": "answer_text",
            "info": "extra_info",
        }
        assert error_result.error == "ValueError: Test error"
