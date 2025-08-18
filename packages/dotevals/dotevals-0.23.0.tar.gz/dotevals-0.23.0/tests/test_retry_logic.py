"""Tests for retry logic on connection errors."""

import asyncio
import tempfile
from pathlib import Path

import pytest
from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from dotevals import ForEach
from dotevals.concurrency import SlidingWindow
from dotevals.metrics import accuracy
from dotevals.models import Result, Score
from dotevals.sessions import SessionManager


class MockConnectionError(ConnectionError):
    """Mock connection error for testing."""

    pass


def test_sync_retry_on_connection_error():
    """Test that sync evaluation retries on connection errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1"), ("Q2", "A2")]

        # Create a mock that fails twice then succeeds
        attempt_count = 0

        # Create ForEach instance with custom retry configuration
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(4),  # 1 initial + 3 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            )
        )

        @foreach("question,answer", test_data)
        def eval_with_retry(question, answer):
            nonlocal attempt_count
            attempt_count += 1

            if question == "Q2" and attempt_count < 3:
                raise MockConnectionError("Connection failed")

            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_with_retry(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    # Should succeed after retries
    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is None
    assert attempt_count == 3  # 1 for Q1, 2 failed + 1 success for Q2


def test_sync_retry_exhaustion():
    """Test that sync evaluation fails after exhausting retries."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom retry configuration
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(3),  # 1 initial + 2 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            )
        )

        @foreach("question,answer", test_data)
        def eval_always_fails(question, answer):
            nonlocal attempt_count
            attempt_count += 1
            raise MockConnectionError("Connection permanently failed")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_always_fails(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    # Should fail after exhausting retries
    assert len(result.results) == 1
    assert result.results[0].error is not None
    assert "MockConnectionError" in result.results[0].error
    assert attempt_count == 3  # Initial attempt + 2 retries


def test_sync_no_retry_on_other_errors():
    """Test that sync evaluation doesn't retry on non-connection errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom retry configuration that only retries on connection errors
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(4),  # 1 initial + 3 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        def eval_with_value_error(question, answer):
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Not a connection error")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_with_value_error(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    # Should fail immediately without retries
    assert len(result.results) == 1
    assert result.results[0].error is not None
    assert "ValueError" in result.results[0].error
    assert attempt_count == 1  # No retries


def test_sync_configurable_retry_parameters():
    """Test configurable retry parameters for sync evaluation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom retry configuration
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(2),  # 1 initial + 1 retry
                wait=wait_exponential_jitter(initial=0.1, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        def eval_with_custom_retry(question, answer):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 2:
                raise MockConnectionError("Connection failed")

            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        # Test with custom retry count
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_with_custom_retry(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    assert len(result.results) == 1
    assert result.results[0].error is None
    assert attempt_count == 2  # Initial + 1 retry


def test_sync_disable_retry():
    """Test disabling retry logic by setting max_retries to 0."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with no retries
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(1),  # No retries, only initial attempt
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        def eval_no_retry(question, answer):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count == 1:
                raise MockConnectionError("Connection failed")

            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_no_retry(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    # Should fail immediately without retries
    assert len(result.results) == 1
    assert result.results[0].error is not None
    assert attempt_count == 1  # No retries


@pytest.mark.asyncio
async def test_async_retry_on_connection_error():
    """Test that async evaluation retries on connection errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1"), ("Q2", "A2")]

        attempt_count = 0

        # Create ForEach instance with custom async retry configuration
        foreach = ForEach(
            retries=AsyncRetrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(4),  # 1 initial + 3 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        async def async_eval_with_retry(question, answer):
            nonlocal attempt_count
            attempt_count += 1

            if question == "Q2" and attempt_count < 3:
                raise MockConnectionError("Connection failed")

            await asyncio.sleep(0.01)  # Simulate async work
            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        result = await async_eval_with_retry(
            session_manager=session_manager, samples=None
        )

    # Should succeed after retries
    assert len(result.results) == 2
    assert result.results[0].error is None
    assert result.results[1].error is None
    assert attempt_count >= 3  # At least 3 attempts


@pytest.mark.asyncio
async def test_async_retry_exhaustion():
    """Test that async evaluation fails after exhausting retries."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom async retry configuration
        foreach = ForEach(
            retries=AsyncRetrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(3),  # 1 initial + 2 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        async def async_eval_always_fails(question, answer):
            nonlocal attempt_count
            attempt_count += 1
            await asyncio.sleep(0.01)
            raise MockConnectionError("Connection permanently failed")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        result = await async_eval_always_fails(
            session_manager=session_manager, samples=None
        )

    # Should fail after exhausting retries
    assert len(result.results) == 1
    assert result.results[0].error is not None
    assert "MockConnectionError" in result.results[0].error
    assert attempt_count == 3  # Initial attempt + 2 retries


@pytest.mark.asyncio
async def test_async_no_retry_on_other_errors():
    """Test that async evaluation doesn't retry on non-connection errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom async retry configuration that only retries on connection errors
        foreach = ForEach(
            retries=AsyncRetrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(4),  # 1 initial + 3 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        async def async_eval_with_value_error(question, answer):
            nonlocal attempt_count
            attempt_count += 1
            await asyncio.sleep(0.01)
            raise ValueError("Not a connection error")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        result = await async_eval_with_value_error(
            session_manager=session_manager, samples=None
        )

    # Should fail immediately without retries
    assert len(result.results) == 1
    assert result.results[0].error is not None
    assert "ValueError" in result.results[0].error
    assert attempt_count == 1  # No retries


@pytest.mark.asyncio
async def test_async_concurrent_retries():
    """Test that concurrent async evaluations can retry independently."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [(f"Q{i}", f"A{i}") for i in range(5)]

        attempt_counts = {}

        # Create ForEach instance with custom async retry configuration and concurrency
        foreach = ForEach(
            retries=AsyncRetrying(
                retry=retry_if_exception_type((MockConnectionError,)),
                stop=stop_after_attempt(4),  # 1 initial + 3 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
            concurrency=SlidingWindow(max_concurrency=3),
        )

        @foreach("question,answer", test_data)
        async def async_eval_concurrent(question, answer):
            if question not in attempt_counts:
                attempt_counts[question] = 0
            attempt_counts[question] += 1

            # Q2 and Q4 fail once
            if question in ["Q2", "Q4"] and attempt_counts[question] < 2:
                raise MockConnectionError(f"Connection failed for {question}")

            await asyncio.sleep(0.01)
            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        result = await async_eval_concurrent(
            session_manager=session_manager, samples=None
        )

    # All should succeed
    assert len(result.results) == 5
    assert all(r.error is None for r in result.results)
    assert attempt_counts["Q2"] == 2  # Failed once, then succeeded
    assert attempt_counts["Q4"] == 2  # Failed once, then succeeded


def test_retry_on_timeout_error():
    """Test that TimeoutError is retried."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom retry configuration for TimeoutError
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((TimeoutError,)),
                stop=stop_after_attempt(3),  # 1 initial + 2 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        def eval_with_timeout(question, answer):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 2:
                raise TimeoutError("Request timed out")

            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_with_timeout(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    assert len(result.results) == 1
    assert result.results[0].error is None
    assert attempt_count == 2


def test_retry_on_os_error():
    """Test that OSError (network-related) is retried."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        attempt_count = 0

        # Create ForEach instance with custom retry configuration for OSError
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((OSError,)),
                stop=stop_after_attempt(3),  # 1 initial + 2 retries
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        def eval_with_os_error(question, answer):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 2:
                raise OSError("Network is unreachable")

            return Result(Score("test", True, [accuracy()]), prompt=f"Q: {question}")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_with_os_error(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    assert len(result.results) == 1
    assert result.results[0].error is None
    assert attempt_count == 2


def test_retry_preserves_original_error():
    """Test that the original error message is preserved after retry exhaustion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1")]

        # Create ForEach instance with custom retry configuration
        foreach = ForEach(
            retries=Retrying(
                retry=retry_if_exception_type((ConnectionError,)),
                stop=stop_after_attempt(2),  # 1 initial + 1 retry
                wait=wait_exponential_jitter(initial=0.01, max=0.1),
                reraise=True,
            ),
        )

        @foreach("question,answer", test_data)
        def eval_with_specific_error(question, answer):
            raise ConnectionError("Specific connection error message")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_experiment_{unique_id}",
            storage=f"json://{storage_path}",
        )
        coro = eval_with_specific_error(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

    assert len(result.results) == 1
    assert result.results[0].error is not None
    assert "Specific connection error message" in result.results[0].error
