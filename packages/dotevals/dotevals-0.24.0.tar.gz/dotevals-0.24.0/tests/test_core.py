"""Refactored core tests - more concise with single responsibility per test."""

import asyncio

# Removed Mock import - using real implementations
import pytest
from tenacity import AsyncRetrying, Retrying, stop_after_attempt

from dotevals import ForEach, foreach
from dotevals.concurrency import SlidingWindow
from dotevals.core import run_evaluation
from dotevals.evaluators import evaluator, exact_match
from dotevals.metrics import Metric, accuracy, metric, registry
from dotevals.models import Result, Score
from dotevals.sessions import SessionManager


@pytest.fixture
def simple_dataset():
    """Basic 3-item dataset for testing."""
    return [("a", 1), ("b", 2), ("c", 3)]


@pytest.fixture
def large_dataset():
    """100-item dataset for sampling tests."""
    return [(str(i), i) for i in range(100)]


@pytest.fixture
def session_manager(tmp_path):
    """Session manager with JSON storage."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return SessionManager(
        evaluation_name=f"test_eval_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )


@metric
def mean():
    """Custom mean metric for testing."""

    def metric_fn(scores: list[float]) -> float:
        return sum(scores) / len(scores) if scores else 0.0

    return metric_fn


@metric
def metric_any():
    """Custom any metric for testing."""

    def metric_fn(scores: list[bool]) -> bool:
        return any(scores)

    return metric_fn


@pytest.fixture(autouse=True)
def register_test_metrics():
    """Register custom metrics for tests and clean up after."""
    # Register custom metrics
    registry["mean"] = mean()
    registry["metric_any"] = metric_any()
    yield
    # Clean up after test
    if "mean" in registry:
        del registry["mean"]
    if "metric_any" in registry:
        del registry["metric_any"]


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.asyncio
async def test_basic_evaluation(simple_dataset, session_manager, is_async):
    """Test basic evaluation works for both sync and async."""
    if is_async:

        @foreach("text,number", simple_dataset)
        async def eval_fn(text, number):
            await asyncio.sleep(0)  # Simulate async work
            return Result(exact_match(text, text))
    else:

        @foreach("text,number", simple_dataset)
        def eval_fn(text, number):
            return Result(exact_match(text, text))

    summary = await eval_fn(session_manager, samples=None)

    assert summary.summary["exact_match"]["accuracy"] == 1.0
    assert len(summary.results) == 3  # Check results count instead


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("samples", [0, 5, 50, 200])
@pytest.mark.asyncio
async def test_sampling(large_dataset, session_manager, is_async, samples):
    """Test sampling parameter works correctly."""
    if is_async:

        @foreach("text,number", large_dataset)
        async def eval_fn(text, number):
            return Result(exact_match(int(text), number))
    else:

        @foreach("text,number", large_dataset)
        def eval_fn(text, number):
            return Result(exact_match(int(text), number))

    summary = await eval_fn(session_manager, samples=samples)

    expected_count = min(samples, 100) if samples > 0 else 0
    assert len(summary.results) == expected_count


@pytest.mark.parametrize(
    "dataset,columns,expected_calls",
    [
        # Single column with tuple
        ([("a",), ("b",)], "text", [{"text": "a"}, {"text": "b"}]),
        # Single column with direct values
        (["a", "b"], "text", [{"text": "a"}, {"text": "b"}]),
        # Multiple columns
        (
            [("a", 1), ("b", 2)],
            "text,num",
            [{"text": "a", "num": 1}, {"text": "b", "num": 2}],
        ),
        # Dict dataset
        ([{"x": 1}, {"x": 2}], "data", [{"data": {"x": 1}}, {"data": {"x": 2}}]),
        # Many columns (6 columns test)
        (
            [("a", "b", "c", "d", "e", "f")],
            "c1,c2,c3,c4,c5,c6",
            [{"c1": "a", "c2": "b", "c3": "c", "c4": "d", "c5": "e", "c6": "f"}],
        ),
    ],
)
@pytest.mark.asyncio
async def test_dataset_formats(dataset, columns, expected_calls, session_manager):
    """Test different dataset formats are handled correctly."""
    captured_args = []

    @foreach(columns, dataset)
    def eval_fn(**kwargs):
        captured_args.append(kwargs)
        return Result(Score("test", True, [accuracy()]))

    await eval_fn(session_manager, samples=None)

    assert len(captured_args) == len(expected_calls)
    for actual, expected in zip(captured_args, expected_calls):
        assert actual == expected


@pytest.mark.asyncio
async def test_empty_dataset(session_manager):
    """Test empty dataset returns empty summary."""

    @foreach("text", [])
    def eval_fn(text):
        return Result(exact_match(text, text))

    summary = await eval_fn(session_manager, samples=None)
    assert summary.summary == {}
    assert len(summary.results) == 0


@pytest.mark.asyncio
async def test_multiple_evaluators(simple_dataset, session_manager):
    """Test multiple evaluators in single result."""

    @foreach("text,number", simple_dataset)
    def eval_fn(text, number):
        return Result(
            exact_match(text, text, name="text_match"),
            exact_match(number, number, name="number_match"),
            prompt=text,
        )

    summary = await eval_fn(session_manager, samples=None)

    assert "text_match" in summary.summary
    assert "number_match" in summary.summary
    assert summary.summary["text_match"]["accuracy"] == 1.0
    assert summary.summary["number_match"]["accuracy"] == 1.0


@pytest.mark.asyncio
async def test_multiple_metrics(simple_dataset, session_manager):
    """Test multiple metrics on single evaluator."""
    mean_metric = mean()

    @evaluator(metrics=[accuracy(), mean_metric])
    def value_eval(value, target):
        return value == target

    @foreach("text,number", simple_dataset)
    def eval_fn(text, number):
        # Pass 1.0 for first item, 0.0 for second, 1.0 for third -> mean = 2/3
        return Result(value_eval(number, number if number != 2 else -1))

    summary = await eval_fn(session_manager, samples=None)

    assert summary.summary["value_eval"]["accuracy"] == pytest.approx(2 / 3)
    assert summary.summary["value_eval"]["mean"] == pytest.approx(2 / 3)


@pytest.mark.asyncio
async def test_custom_metric_any(simple_dataset, session_manager):
    """Test custom metric_any aggregation."""

    @evaluator(metrics=[accuracy(), metric_any()])
    def dummy_match(answer, target):
        return answer == target

    @foreach("text,number", simple_dataset)
    def eval_fn(text, number):
        # Will match only first item where text=="a"
        return Result(dummy_match(text, "a"))

    summary = await eval_fn(session_manager, samples=None)

    assert summary.summary["dummy_match"]["accuracy"] == pytest.approx(1 / 3)
    assert summary.summary["dummy_match"]["metric_any"] is True


@pytest.mark.asyncio
async def test_evaluation_error_handling(simple_dataset, session_manager):
    """Test errors are captured in results."""
    call_count = 0

    @foreach("text,number", simple_dataset)
    def eval_fn(text, number):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise ValueError("Test error")
        return Result(exact_match(text, text))

    summary = await eval_fn(session_manager, samples=None)

    # Check we have 3 total results: 2 successful and 1 error
    assert len(summary.results) == 3
    assert len([r for r in summary.results if not r.error]) == 2  # 2 successful results
    error_results = [r for r in summary.results if r.error]
    assert len(error_results) == 1
    assert "ValueError: Test error" in error_results[0].error

    # Accuracy should be calculated only on the 2 successful results (both are True)
    # Since only 2 items were evaluated successfully, accuracy = 2/3
    assert summary.summary["exact_match"]["accuracy"] == pytest.approx(2 / 3)


@pytest.mark.asyncio
async def test_sync_retry_configuration(tmp_path):
    """Test sync evaluation with custom retry configuration."""
    foreach_with_retry = ForEach(retries=Retrying(stop=stop_after_attempt(5)))

    attempt_count = 0

    @foreach_with_retry("text", [("a",)])
    def eval_fn(text):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Retry me")
        return Result(exact_match(text, "a"))

    # Use real SessionManager with temporary storage
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    session_manager = SessionManager(
        experiment_name=f"test_retry_{unique_id}",
        evaluation_name=f"test_eval_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )

    summary = await eval_fn(session_manager, samples=None)
    assert attempt_count == 3
    # Verify the result was successful after retries
    assert summary.summary["exact_match"]["accuracy"] == 1.0


@pytest.mark.asyncio
async def test_async_retry_configuration(tmp_path):
    """Test async evaluation with custom retry configuration."""
    foreach_with_retry = ForEach(retries=AsyncRetrying(stop=stop_after_attempt(5)))

    attempt_count = 0

    @foreach_with_retry("text", [("a",)])
    async def eval_fn(text):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Retry me")
        return Result(exact_match(text, "a"))

    # Use real SessionManager with temporary storage
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    session_manager = SessionManager(
        experiment_name=f"test_async_retry_{unique_id}",
        evaluation_name=f"test_eval_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )

    summary = await eval_fn(session_manager, samples=None)
    assert attempt_count == 3
    # Verify the result was successful after retries
    assert summary.summary["exact_match"]["accuracy"] == 1.0


@pytest.mark.asyncio
async def test_async_evaluation_without_retry(tmp_path):
    """Test async evaluation without retry on exceptions."""
    from tenacity import AsyncRetrying, stop_after_attempt

    # Create a no-retry configuration (single attempt only)
    no_retry = AsyncRetrying(stop=stop_after_attempt(1))
    foreach_no_retry = ForEach(retries=no_retry)

    @foreach_no_retry("text", [("a",)])
    async def eval_fn(text):
        raise ConnectionError("Should not retry")

    # Use real SessionManager with temporary storage
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    session_manager = SessionManager(
        experiment_name=f"test_no_retry_{unique_id}",
        evaluation_name=f"test_eval_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )

    # Should complete without retrying (error captured in result)
    summary = await eval_fn(session_manager, samples=None)
    # Verify error was captured in results
    assert len(summary.results) == 1
    assert summary.results[0].error is not None
    assert "ConnectionError" in summary.results[0].error


@pytest.mark.asyncio
async def test_async_evaluation_with_exceptions(tmp_path):
    """Test async evaluation handles exceptions properly."""

    @foreach("text", [("a",), ("b",), ("c",)])
    async def eval_fn(text):
        if text == "b":
            raise RuntimeError("Expected error")
        return Result(exact_match(text, text))

    # Use real SessionManager with temporary storage
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    session_manager = SessionManager(
        experiment_name=f"test_exceptions_{unique_id}",
        evaluation_name=f"test_eval_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )

    summary = await eval_fn(session_manager, samples=None)
    # Should have processed all 3 items (2 success, 1 error)
    assert len(summary.results) == 3
    # Check that we have 2 successful results and 1 error
    errors = [r for r in summary.results if r.error is not None]
    successes = [r for r in summary.results if r.error is None]
    assert len(errors) == 1
    assert len(successes) == 2
    assert "RuntimeError" in errors[0].error


@pytest.mark.asyncio
async def test_additional_kwargs_passed_through(simple_dataset, session_manager):
    """Test additional kwargs are passed to evaluation function."""
    captured_kwargs = []

    @foreach("text,number", simple_dataset)
    def eval_fn(text, number, custom_param=None, another_param=42):
        captured_kwargs.append(
            {"custom_param": custom_param, "another_param": another_param}
        )
        return Result(exact_match(text, text))

    await eval_fn(
        session_manager, samples=None, custom_param="test_value", another_param=100
    )

    assert len(captured_kwargs) == 3
    for kwargs in captured_kwargs:
        assert kwargs["custom_param"] == "test_value"
        assert kwargs["another_param"] == 100


@pytest.mark.asyncio
async def test_sample_order_preserved_sync(large_dataset, session_manager):
    """Test sync evaluation preserves dataset order."""
    processed_order = []

    @foreach("text,number", large_dataset)
    def eval_fn(text, number):
        processed_order.append(number)
        return Result(exact_match(True, True))

    await eval_fn(session_manager, samples=10)

    assert processed_order == list(range(10))


@pytest.mark.asyncio
async def test_sample_order_may_vary_async(large_dataset, session_manager):
    """Test async evaluation may process out of order."""
    processed_order = []

    @foreach("text,number", large_dataset)
    async def eval_fn(text, number):
        # Add variable delay to encourage out-of-order processing
        await asyncio.sleep(0.001 * (10 - number) if number < 10 else 0)
        processed_order.append(number)
        return Result(exact_match(True, True))

    await eval_fn(session_manager, samples=10)

    assert len(processed_order) == 10
    assert set(processed_order) == set(range(10))


@pytest.mark.asyncio
async def test_run_evaluation_directly_with_samples(large_dataset, session_manager):
    """Test calling run_evaluation directly with samples parameter."""

    def eval_fn(text, number):
        return Result(exact_match(int(text), number))

    summary = await run_evaluation(
        eval_fn, "text,number", large_dataset, session_manager, samples=5
    )

    assert len(summary.results) == 5


@pytest.mark.asyncio
async def test_evaluation_with_session_manager(simple_dataset, tmp_path):
    """Test evaluation with explicit session manager configuration."""
    session_mgr = SessionManager(
        storage=f"json://{tmp_path}",
        experiment_name="test_exp",
        evaluation_name="test_eval",
    )

    @foreach("text,number", simple_dataset)
    def eval_fn(text, number):
        return Result(exact_match(text, text))

    result = await eval_fn(session_manager=session_mgr, samples=None)

    assert isinstance(result.summary, dict)
    assert result.summary["exact_match"]["accuracy"] == 1.0


@pytest.mark.asyncio
async def test_async_evaluation_with_session_manager(simple_dataset, tmp_path):
    """Test async evaluation with explicit session manager configuration."""
    session_mgr = SessionManager(
        storage=f"json://{tmp_path}",
        experiment_name="test_exp",
        evaluation_name="test_eval",
    )

    @foreach("text,number", simple_dataset)
    async def eval_fn(text, number):
        await asyncio.sleep(0.001)
        return Result(exact_match(text, text))

    result = await eval_fn(session_manager=session_mgr, samples=None)

    assert isinstance(result.summary, dict)
    assert result.summary["exact_match"]["accuracy"] == 1.0


@pytest.mark.asyncio
async def test_async_evaluator_partial_failure(tmp_path):
    """Test handling partial failures in async evaluation."""
    import uuid

    from dotevals.sessions import SessionManager

    unique_id = str(uuid.uuid4())[:8]
    session_mgr = SessionManager(
        evaluation_name=f"test_eval_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}",
    )

    call_count = 0

    async def sometimes_failing(input):  # Parameter name must match column name
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise ValueError(f"Failed on item {call_count}")
        return Result(Score("test", True, []))

    dataset = [{"input": f"test_{i}"} for i in range(3)]

    # Errors are captured in results, not propagated
    from dotevals.concurrency import AsyncSequential

    summary = await run_evaluation(
        sometimes_failing,
        "input",  # column_spec should be a string
        dataset,
        session_manager=session_mgr,
        concurrency=AsyncSequential(),  # Use AsyncSequential for async evaluator
    )

    # Check that we have 2 successful results and 1 error
    assert len(summary.results) == 3
    successful = [r for r in summary.results if not r.error]
    errors = [r for r in summary.results if r.error]

    assert len(successful) == 2
    assert len(errors) == 1

    # The second item should have failed
    assert errors[0].dataset_row == {"input": {"input": "test_1"}}
    assert "ValueError" in errors[0].error
    assert "Failed on item 2" in errors[0].error


@pytest.mark.asyncio
async def test_async_concurrent_evaluation_errors(tmp_path):
    """Test error handling with concurrent async evaluation."""
    import uuid

    from dotevals.sessions import SessionManager

    unique_id = str(uuid.uuid4())[:8]
    session_mgr = SessionManager(
        experiment_name=f"test_exp_{unique_id}",
        evaluation_name=f"test_eval_{unique_id}",
        storage=f"json://{tmp_path}",
    )

    async def evaluator_with_errors(id):  # Parameter name must match column name
        if id % 3 == 0:
            raise ValueError(f"Error on {id}")
        await asyncio.sleep(0.01)
        return Result(Score("test", id, []))

    dataset = [(i,) for i in range(10)]  # Use tuples for single column

    # Errors are captured in results, not propagated
    from dotevals.concurrency import Adaptive

    summary = await run_evaluation(
        evaluator_with_errors,
        "id",  # column_spec should be a string
        dataset,
        session_manager=session_mgr,
        concurrency=Adaptive(initial_concurrency=3),  # Use Adaptive strategy for async
    )

    # Check that we have both successful and error results
    successful = [r for r in summary.results if not r.error]
    errors = [r for r in summary.results if r.error]

    # IDs 0, 3, 6, 9 should have errors (multiples of 3)
    assert len(errors) == 4
    assert len(successful) == 6

    # Check error messages
    for error_result in errors:
        assert "ValueError" in error_result.error
        assert "Error on" in error_result.error
