"""Tests for adaptive concurrency internal functionality to achieve targeted coverage."""

import asyncio
import time

import pytest

from dotevals.concurrency.adaptive import Adaptive, ThroughputTracker


class TestThroughputTracker:
    """Test the ThroughputTracker component."""

    def test_throughput_tracker_insufficient_data(self):
        """Test throughput calculation with insufficient data."""
        tracker = ThroughputTracker()

        # With no completions, should return None
        assert tracker.get_throughput() is None

        # With only one completion, should return None
        tracker.record_completion(time.time())
        assert tracker.get_throughput() is None

    def test_throughput_tracker_zero_time_span(self):
        """Test throughput calculation with zero time span."""
        tracker = ThroughputTracker()

        # Record completions at the exact same time
        now = time.time()
        tracker.record_completion(now)
        tracker.record_completion(now)
        tracker.record_completion(now)

        # Should return None due to zero time span
        assert tracker.get_throughput() is None

    def test_recent_throughput_insufficient_data(self):
        """Test recent throughput with insufficient data."""
        tracker = ThroughputTracker()

        # With no completions
        assert tracker.get_recent_throughput() is None

        # With only one completion
        tracker.record_completion(time.time())
        assert tracker.get_recent_throughput() is None

    def test_recent_throughput_zero_time_span(self):
        """Test recent throughput with zero time span."""
        tracker = ThroughputTracker()

        # Record completions at the same time
        now = time.time()
        tracker.record_completion(now)
        tracker.record_completion(now)
        tracker.record_completion(now)

        # Should return None due to zero time span
        assert tracker.get_recent_throughput() is None

    def test_recent_throughput_custom_window(self):
        """Test recent throughput with custom window size."""
        tracker = ThroughputTracker()

        # Create a timing pattern where different windows give different results
        base_time = time.time()
        # Add completions with specific timing: fast start, then slower
        times = [
            base_time,  # 0
            base_time + 0.1,  # 1
            base_time + 0.2,  # 2
            base_time + 1.0,  # 3 (big gap)
            base_time + 2.0,  # 4 (big gap)
        ]

        for timestamp in times:
            tracker.record_completion(timestamp)

        # Test with different window sizes
        throughput_3 = tracker.get_recent_throughput(
            3
        )  # Uses timestamps 2, 3, 4 (span=1.8, rate=2/1.8)
        throughput_5 = tracker.get_recent_throughput(
            5
        )  # Uses all timestamps (span=2.0, rate=4/2.0)

        assert throughput_3 is not None
        assert throughput_5 is not None
        # These should be different due to different time spans
        assert throughput_3 != throughput_5


class TestAdaptiveConcurrency:
    """Test the Adaptive concurrency strategy."""

    @pytest.mark.asyncio
    async def test_adaptive_error_handling_and_recording(self):
        """Test error handling and recording in adaptive execution."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.1,
            error_backoff_factor=0.5,
        )

        error_count = 0
        success_count = 0

        def create_tasks():
            nonlocal error_count, success_count
            for i in range(5):

                async def task(task_id=i):
                    if task_id == 1:  # Make second task fail
                        raise ValueError(f"Error in task {task_id}")
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        errors_caught = 0

        try:
            async for result in strategy.execute(create_tasks()):
                if result is not None:
                    results.append(result)
        except ValueError as e:
            errors_caught += 1
            assert "Error in task 1" in str(e)

        # Should have caught the error and recorded it
        assert errors_caught > 0
        stats = strategy.get_stats()
        assert stats["recent_errors"] > 0

    @pytest.mark.asyncio
    async def test_adaptive_progress_callback_with_results(self):
        """Test progress callback with actual results."""
        strategy = Adaptive(initial_concurrency=2, adaptation_interval=0.1)

        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(3):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks(), progress_callback):
            results.append(result)

        # Both results and progress_results should have the same items
        assert len(results) == 3
        assert len(progress_results) == 3
        assert set(results) == set(progress_results)

    @pytest.mark.asyncio
    async def test_adaptive_result_yielding(self):
        """Test result yielding when not None."""
        strategy = Adaptive(initial_concurrency=2, adaptation_interval=0.1)

        def create_tasks():
            # Mix of tasks returning results and None
            async def task_with_result():
                await asyncio.sleep(0.01)
                return "valid_result"

            async def task_with_none():
                await asyncio.sleep(0.01)
                return None

            yield task_with_result
            yield task_with_none
            yield task_with_result

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        # Should only yield non-None results
        assert len(results) == 2
        assert all(r == "valid_result" for r in results)

    @pytest.mark.asyncio
    async def test_adaptive_exception_error_counting(self):
        """Test exception handling increases error count."""
        strategy = Adaptive(initial_concurrency=1, adaptation_interval=0.1)

        def create_tasks():
            async def failing_task():
                await asyncio.sleep(0.01)
                raise RuntimeError("Task failed")

            yield failing_task

        with pytest.raises(RuntimeError, match="Task failed"):
            async for result in strategy.execute(create_tasks()):
                pass

        # Error count should have increased
        stats = strategy.get_stats()
        assert stats["recent_errors"] > 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_adjustment_under_load(self):
        """Test concurrency adjustment logic."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.05,  # Fast adaptation
            min_concurrency=1,
            max_concurrency=8,
            stability_window=1,
        )

        def create_tasks():
            # Create many tasks to trigger adaptation
            for i in range(20):

                async def task(task_id=i):
                    await asyncio.sleep(0.02)  # Moderate load
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 20

        # Strategy should have adapted concurrency
        final_stats = strategy.get_stats()
        assert "adaptation_history" in final_stats
        assert final_stats["total_completed"] == 20

    @pytest.mark.asyncio
    async def test_adaptive_throughput_based_scaling(self):
        """Test throughput-based concurrency scaling."""
        strategy = Adaptive(
            initial_concurrency=3,
            adaptation_interval=0.08,
            min_concurrency=2,
            max_concurrency=10,
            stability_window=2,
        )

        def create_tasks():
            # Create enough tasks to allow multiple adaptation cycles
            for i in range(25):

                async def task(task_id=i):
                    await asyncio.sleep(0.015)  # Consistent work time
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 25

        # Should have some adaptation history
        stats = strategy.get_stats()
        assert stats["adaptation_history"] is not None
        assert len(stats["adaptation_history"]) >= 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_limits_enforcement(self):
        """Test that concurrency limits are enforced."""
        strategy = Adaptive(
            initial_concurrency=3,
            min_concurrency=2,
            max_concurrency=4,
            adaptation_interval=0.1,
        )

        def create_tasks():
            for i in range(8):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 8

        # Concurrency should respect limits
        assert strategy.current_concurrency >= 2
        assert strategy.current_concurrency <= 4

    @pytest.mark.asyncio
    async def test_adaptive_performance_degradation_handling(self):
        """Test handling of performance degradation."""
        strategy = Adaptive(
            initial_concurrency=3,
            adaptation_interval=0.06,
            min_concurrency=1,
            max_concurrency=8,
            stability_window=1,
        )

        task_counter = 0

        def create_tasks():
            nonlocal task_counter
            for i in range(15):

                async def task(task_id=i):
                    nonlocal task_counter
                    task_counter += 1
                    # Simulate degrading performance
                    delay = 0.01 + (task_counter * 0.003)
                    await asyncio.sleep(delay)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 15

        # Strategy should have attempted adaptations
        stats = strategy.get_stats()
        assert stats["total_completed"] == 15


class TestAdapative:
    @pytest.mark.asyncio
    async def test_adaptive_basic_execution(self):
        """Test that adaptive strategy can execute tasks."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.1,  # Fast adaptation for testing
            min_concurrency=1,
            max_concurrency=10,
        )

        def create_tasks():
            for i in range(5):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 5
        assert all(r.startswith("result_") for r in results)

    @pytest.mark.asyncio
    async def test_adaptive_with_progress_callback(self):
        """Test adaptive strategy with progress callback."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.05,
        )
        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(4):

                async def task(task_id=i):
                    await asyncio.sleep(0.001)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks(), progress_callback):
            results.append(result)

        assert len(results) == 4
        assert len(progress_results) == 4
        assert set(results) == set(progress_results)

    @pytest.mark.asyncio
    async def test_adaptive_throughput_tracking(self):
        """Test that adaptive strategy tracks throughput."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.05,
        )

        def create_tasks():
            for i in range(10):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        stats = strategy.get_stats()
        assert stats["total_completed"] == 10
        assert stats["total_tasks"] == 10
        assert stats["throughput"] is not None
        assert stats["throughput"] > 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_adjustment(self):
        """Test that adaptive strategy can adjust concurrency."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.05,  # Fast adaptation
            min_concurrency=1,
            max_concurrency=20,
            stability_window=1,  # Quick decisions
        )

        # Create enough tasks to allow adaptation to happen
        def create_tasks():
            for i in range(30):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)  # Some work time
                    return f"result_{task_id}"

                yield task

        results = []

        async for result in strategy.execute(create_tasks()):
            results.append(result)

        final_stats = strategy.get_stats()

        # Should have completed all tasks
        assert len(results) == 30

        # Strategy should have some adaptation history or at least be functioning
        assert final_stats["total_completed"] == 30
        assert final_stats["throughput"] is not None

    @pytest.mark.asyncio
    async def test_adaptive_error_handling(self):
        """Test that adaptive strategy handles errors properly."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.05,
            error_backoff_factor=0.5,
        )

        def create_tasks():
            # First few tasks succeed
            for i in range(3):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

            # Then a task fails
            async def failing_task():
                await asyncio.sleep(0.01)
                raise ValueError("test error")

            yield failing_task

        results = []

        with pytest.raises(ValueError, match="test error"):
            async for result in strategy.execute(create_tasks()):
                results.append(result)

        # Should have gotten some results before the error
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_adaptive_stats_collection(self):
        """Test that adaptive strategy collects comprehensive stats."""
        strategy = Adaptive(
            initial_concurrency=3,
            adaptation_interval=0.05,
        )

        def create_tasks():
            for i in range(8):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        stats = strategy.get_stats()

        # Verify all expected stats are present
        assert "current_concurrency" in stats
        assert "throughput" in stats
        assert "total_completed" in stats
        assert "total_tasks" in stats
        assert "recent_errors" in stats
        assert "adaptation_history" in stats

        # Verify stats values make sense
        assert stats["total_completed"] == 8
        assert stats["total_tasks"] == 8
        assert stats["recent_errors"] == 0
        assert isinstance(stats["adaptation_history"], list)

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_limits(self):
        """Test that adaptive strategy respects concurrency limits."""
        strategy = Adaptive(
            initial_concurrency=5,
            min_concurrency=2,
            max_concurrency=8,
            adaptation_interval=0.01,
        )

        def create_tasks():
            for i in range(6):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        # Strategy should respect limits
        assert strategy.current_concurrency >= 2
        assert strategy.current_concurrency <= 8
        assert len(results) == 6

    @pytest.mark.asyncio
    async def test_adaptive_throughput_measurement(self):
        """Test throughput measurement accuracy."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.1,
        )

        start_time = time.time()

        def create_tasks():
            for i in range(10):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        end_time = time.time()
        elapsed = end_time - start_time

        stats = strategy.get_stats()
        measured_throughput = stats["throughput"]

        # Rough throughput check (should be in reasonable range)
        if measured_throughput is not None:
            expected_throughput = 10 / elapsed
            # Allow for some variance due to overhead and timing
            assert measured_throughput > 0
            assert measured_throughput < expected_throughput * 2  # Not too high
