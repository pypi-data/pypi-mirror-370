"""Test async evaluation execution in pytest plugin context."""

import asyncio
import json
import subprocess

from dotevals.core import foreach
from dotevals.evaluators import exact_match
from dotevals.models import Result


def test_async_evaluation_executes_and_saves_results(tmp_path):
    """Test that async evaluation functions are properly executed and results are saved."""
    # Create a test file with an async evaluation
    test_file = tmp_path / "test_async_eval.py"
    test_file.write_text(
        """
import asyncio
from pathlib import Path
from dotevals.core import ForEach
from dotevals.evaluators import exact_match
from dotevals.models import Result
from dotevals.storage.json import JSONStorage

dataset = [("hello", "hello"), ("world", "world")]

# Create custom ForEach with storage configuration
custom_foreach = ForEach()

@custom_foreach("input,expected", dataset)
async def test_async_evaluation(input, expected):
    # Add a small delay to ensure it's truly async
    await asyncio.sleep(0.001)

    # Create a marker file to prove this code executed
    marker = Path("async_eval_ran.txt")
    marker.write_text(f"Evaluated: {input}")

    return Result(
        exact_match(input, expected),
        prompt=f"Test: {input}"
    )
"""
    )

    # Run pytest on the test file with a session
    import subprocess

    result = subprocess.run(
        [
            "pytest",
            str(test_file),
            "-v",
            "--experiment",
            "test_async_experiment",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # Check that the test passed
    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"
    assert "1 passed" in result.stdout

    # Check that the async code actually ran
    marker_file = tmp_path / "async_eval_ran.txt"
    assert marker_file.exists(), "Async evaluation did not run"

    # Check that results were saved - should be in .dotevals directory with experiment name
    doteval_dir = tmp_path / ".dotevals"
    assert doteval_dir.exists(), "No .dotevals directory created"

    experiment_dir = doteval_dir / "test_async_experiment"
    assert experiment_dir.exists(), f"Experiment directory not found in {doteval_dir}"

    # Check for evaluation files
    eval_files = list(experiment_dir.glob("*.jsonl"))
    assert len(eval_files) > 0, f"No evaluation files found in {experiment_dir}"

    # Read JSONL file - use the first file found
    eval_file = eval_files[0]
    with open(eval_file) as f:
        lines = f.readlines()

    # First line is metadata
    metadata = json.loads(lines[0])
    assert metadata["evaluation_name"] == "test_async_evaluation[None-None]"
    assert metadata["status"] == "completed"

    # Remaining lines are results (filter out empty lines)
    results = [json.loads(line) for line in lines[1:] if line.strip()]
    assert len(results) == 2  # Two items in dataset

    # Verify the results content (order may vary due to async execution)
    inputs_found = [result["dataset_row"]["input"] for result in results]
    assert sorted(inputs_found) == ["hello", "world"]

    for result in results:
        assert (
            result["result"]["scores"][0]["value"] is True
        )  # exact_match should be True


def test_async_evaluation_with_concurrency(tmp_path):
    """Test async evaluation with concurrent execution."""
    test_file = tmp_path / "test_async_concurrent.py"
    test_file.write_text(
        """
import asyncio
from dotevals.core import ForEach
from dotevals.evaluators import exact_match
from dotevals.models import Result
from dotevals.storage.json import JSONStorage
from dotevals.concurrency import SlidingWindow

# Larger dataset to test concurrency
dataset = [(f"item{i}", f"item{i}") for i in range(10)]

# Create custom ForEach with concurrency configuration
custom_foreach = ForEach(
    concurrency=SlidingWindow(max_concurrency=5)
)

@custom_foreach("input,expected", dataset)
async def test_async_concurrent(input, expected):
    # Simulate some async work
    await asyncio.sleep(0.01)
    return Result(
        exact_match(input, expected),
        prompt=f"Test: {input}"
    )
"""
    )

    result = subprocess.run(
        [
            "pytest",
            str(test_file),
            "-v",
            "--experiment",
            "test_concurrent_experiment",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Test failed: {result.stdout}\n{result.stderr}"

    # Check results - should be in .dotevals directory
    doteval_dir = tmp_path / ".dotevals" / "test_concurrent_experiment"
    assert doteval_dir.exists(), (
        f"Experiment directory not found in {tmp_path / '.dotevals'}"
    )

    # Find the evaluation file
    eval_files = list(doteval_dir.glob("*.jsonl"))
    assert len(eval_files) > 0, f"No evaluation files found in {doteval_dir}"
    eval_file = eval_files[0]

    with open(eval_file) as f:
        lines = f.readlines()

    # Skip metadata line and read results (filter out empty lines)
    results = [json.loads(line) for line in lines[1:] if line.strip()]
    assert len(results) == 10
    # Verify all succeeded
    for result in results:
        assert result["error"] is None
        assert result["result"]["scores"][0]["value"] is True


def test_async_and_sync_evaluations_together(tmp_path):
    """Test that async and sync evaluations can coexist."""
    test_file = tmp_path / "test_mixed_eval.py"
    test_file.write_text(
        """
import asyncio
from dotevals.core import ForEach
from dotevals.evaluators import exact_match
from dotevals.models import Result
from dotevals.storage.json import JSONStorage

dataset = [("test", "test")]

# Create custom ForEach with storage configuration
custom_foreach = ForEach()

@custom_foreach("input,expected", dataset)
def test_sync_evaluation(input, expected):
    return Result(exact_match(input, expected), prompt=f"Sync: {input}")

@custom_foreach("input,expected", dataset)
async def test_async_evaluation(input, expected):
    await asyncio.sleep(0.001)
    return Result(exact_match(input, expected), prompt=f"Async: {input}")
"""
    )

    result = subprocess.run(
        [
            "pytest",
            str(test_file),
            "-v",
            "--experiment",
            "test_mixed_experiment",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "2 passed" in result.stdout

    # Check both results are saved in .dotevals directory
    experiment_dir = tmp_path / ".dotevals" / "test_mixed_experiment"
    assert experiment_dir.exists(), "Experiment directory not found"

    eval_files = list(experiment_dir.glob("*.jsonl"))
    assert len(eval_files) >= 2, (
        f"Expected at least 2 evaluation files, found {len(eval_files)}"
    )


def test_async_evaluation_error_handling(tmp_path):
    """Test that errors in async evaluations are properly handled."""
    test_file = tmp_path / "test_async_error.py"
    test_file.write_text(
        """
import asyncio
from dotevals.core import ForEach
from dotevals.models import Result
from dotevals.storage.json import JSONStorage

dataset = [("good", "good"), ("bad", "bad")]

# Create custom ForEach with storage configuration
custom_foreach = ForEach()

@custom_foreach("input,expected", dataset)
async def test_async_with_error(input, expected):
    await asyncio.sleep(0.001)
    if input == "bad":
        raise ValueError("Intentional error")
    return Result(prompt=f"Test: {input}")
"""
    )

    result = subprocess.run(
        [
            "pytest",
            str(test_file),
            "-v",
            "--experiment",
            "test_error_experiment",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # Test should pass even with errors in evaluation
    assert result.returncode == 0

    # Check that error is recorded in .dotevals directory
    experiment_dir = tmp_path / ".dotevals" / "test_error_experiment"
    assert experiment_dir.exists(), "Experiment directory not found"

    eval_files = list(experiment_dir.glob("*.jsonl"))
    assert len(eval_files) > 0, "No evaluation files found"
    eval_file = eval_files[0]
    with open(eval_file) as f:
        lines = f.readlines()

    # Skip metadata line and read results (filter out empty lines)
    results = [json.loads(line) for line in lines[1:] if line.strip()]
    assert len(results) == 2

    # Sort results by dataset_row to ensure consistent order
    results = sorted(results, key=lambda r: r["dataset_row"]["input"])

    # "bad" should have error
    assert results[0]["error"] is not None
    assert "Intentional error" in results[0]["error"]

    # "good" should succeed
    assert results[1]["error"] is None


def test_async_evaluation_with_asyncio_run_error():
    """Test that our solution handles the asyncio.run() error correctly."""
    # This test verifies that we're not getting the "asyncio.run() cannot be called
    # from a running event loop" error that was the original issue

    # Create a simple async evaluation
    dataset = [("test", "test")]

    @foreach("input,expected", dataset)
    async def async_eval(input, expected):
        await asyncio.sleep(0.001)
        return Result(exact_match(input, expected), prompt=f"Test: {input}")

    # The function should be properly wrapped
    assert hasattr(async_eval, "_column_names")
    assert asyncio.iscoroutinefunction(async_eval.__wrapped__)

    # Calling it should return a coroutine when called with required parameters
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        from dotevals.sessions import SessionManager

        session_manager = SessionManager(
            "test_eval", storage=f"json://{temp_dir}", experiment_name="test_experiment"
        )
        coro = async_eval(session_manager=session_manager, samples=None)
        assert asyncio.iscoroutine(coro)

        # Clean up
        coro.close()
