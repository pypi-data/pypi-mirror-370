"""Adaptive concurrency strategy for async functions."""

import asyncio
import time
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import (
    Optional,
    TypeVar,
)

T = TypeVar("T")


class ThroughputTracker:
    """Tracks throughput metrics for the adaptive strategy."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.completion_times: deque[float] = deque(maxlen=window_size)
        self.window_start_time: float | None = None
        self.total_completed = 0

    def record_completion(self, timestamp: float) -> None:
        """Record a task completion."""
        self.completion_times.append(timestamp)
        self.total_completed += 1
        if self.window_start_time is None:
            self.window_start_time = timestamp

    def get_throughput(self) -> float | None:
        """Calculate current throughput in requests per second."""
        if len(self.completion_times) < 2:
            return None

        # Calculate throughput over the time window
        time_span = self.completion_times[-1] - self.completion_times[0]
        if time_span <= 0:
            return None

        return (len(self.completion_times) - 1) / time_span

    def get_recent_throughput(self, last_n: int = 5) -> float | None:
        """Get throughput for the last N completions."""
        if len(self.completion_times) < min(last_n, 2):
            return None

        recent = list(self.completion_times)[-last_n:]
        time_span = recent[-1] - recent[0]
        if time_span <= 0:
            return None

        return (len(recent) - 1) / time_span


class Adaptive:
    """Adaptive concurrency strategy that dynamically adjusts to maximize throughput.

    This strategy starts with a conservative concurrency level and continuously
    adjusts it based on observed throughput. It uses a hill-climbing approach
    to find the optimal concurrency level for the given workload and system.
    """

    def __init__(
        self,
        initial_concurrency: int = 5,
        min_concurrency: int = 1,
        max_concurrency: int = 100,
        adaptation_interval: float = 2.0,
        throughput_window: int = 20,
        increase_threshold: float = 0.98,
        decrease_threshold: float = 0.90,
        stability_window: int = 3,
        error_backoff_factor: float = 0.7,
    ):
        """Initialize the adaptive strategy.

        Args:
            initial_concurrency: Starting concurrency level
            min_concurrency: Minimum allowed concurrency
            max_concurrency: Maximum allowed concurrency
            adaptation_interval: Seconds between adaptation decisions
            throughput_window: Number of completions to track for throughput
            increase_threshold: Increase if current/previous throughput > this
            decrease_threshold: Decrease if current/previous throughput < this
            stability_window: Number of measurements before changing direction
            error_backoff_factor: Multiply concurrency by this on errors
        """
        self.current_concurrency = initial_concurrency
        self.min_concurrency = min_concurrency
        self.max_concurrency = max_concurrency
        self.adaptation_interval = adaptation_interval
        self.increase_threshold = increase_threshold
        self.decrease_threshold = decrease_threshold
        self.stability_window = stability_window
        self.error_backoff_factor = error_backoff_factor

        # Tracking state
        self.throughput_tracker = ThroughputTracker(throughput_window)
        self.last_adaptation_time = time.time()
        self.last_throughput: float | None = None
        self.consecutive_increases = 0
        self.consecutive_decreases = 0
        self.recent_errors = 0
        self.total_tasks = 0
        self.adaptation_history: list[tuple[float, int, float]] = []

    async def execute(
        self,
        tasks: Iterator[Callable[[], Awaitable[T]]],
        progress_callback: Callable[[T], None] | None = None,
    ) -> AsyncIterator[T]:
        """Execute tasks with adaptive concurrency control.

        Args:
            tasks: An iterator of callables that return awaitable results
            progress_callback: Optional callback to report progress

        Yields:
            Results from executing the tasks
        """
        tasks_iter = iter(tasks)
        pending_tasks = set()
        adaptation_task = asyncio.create_task(self._adaptation_loop())

        try:
            # Initial fill
            for _ in range(self.current_concurrency):
                try:
                    task_func = next(tasks_iter)
                    task: asyncio.Task = asyncio.create_task(
                        self._execute_with_tracking(task_func)
                    )
                    pending_tasks.add(task)
                    self.total_tasks += 1
                except StopIteration:
                    break

            # Main execution loop
            while pending_tasks:
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for completed_task in done:
                    try:
                        result, error = await completed_task
                        if error:
                            self.recent_errors += 1
                        else:
                            self.throughput_tracker.record_completion(time.time())

                        if progress_callback and result is not None:
                            progress_callback(result)

                        if result is not None:
                            yield result
                    except Exception:
                        self.recent_errors += 1
                        raise

                # Add new tasks up to current concurrency
                current_count = len(pending_tasks)
                tasks_to_add = self.current_concurrency - current_count

                for _ in range(tasks_to_add):
                    try:
                        task_func = next(tasks_iter)
                        task = asyncio.create_task(
                            self._execute_with_tracking(task_func)
                        )
                        pending_tasks.add(task)
                        self.total_tasks += 1
                    except StopIteration:
                        break

        finally:
            adaptation_task.cancel()
            for task in pending_tasks:
                task.cancel()
            try:
                await adaptation_task
            except asyncio.CancelledError:
                pass

    async def _execute_with_tracking(
        self, task_func: Callable[[], Awaitable[T]]
    ) -> tuple[T | None, bool]:
        """Execute a task and track its completion."""
        try:
            result = await task_func()
            return result, False
        except Exception:
            # Re-raise the exception so it can be handled in the main loop
            raise

    async def _adaptation_loop(self) -> None:
        """Background task that periodically adjusts concurrency."""
        while True:
            await asyncio.sleep(self.adaptation_interval)
            self._adapt_concurrency()

    def _adapt_concurrency(self) -> None:
        """Adjust concurrency based on throughput measurements."""
        current_throughput = self.throughput_tracker.get_throughput()
        if current_throughput is None:
            return

        # Record adaptation history
        self.adaptation_history.append(
            (time.time(), self.current_concurrency, current_throughput)
        )

        # Handle error backoff
        if self.recent_errors > 0:
            self._decrease_concurrency(
                factor=self.error_backoff_factor**self.recent_errors
            )
            self.recent_errors = 0  # Reset error count
            return

        # Compare with previous throughput
        if self.last_throughput is not None:
            ratio = current_throughput / self.last_throughput

            if ratio > self.increase_threshold:
                # Throughput improved, try increasing
                self.consecutive_decreases = 0
                self.consecutive_increases += 1

                if self.consecutive_increases >= self.stability_window:
                    self._increase_concurrency()
                    self.consecutive_increases = 0

            elif ratio < self.decrease_threshold:
                # Throughput degraded, decrease
                self.consecutive_increases = 0
                self.consecutive_decreases += 1

                if self.consecutive_decreases >= self.stability_window:
                    self._decrease_concurrency()
                    self.consecutive_decreases = 0

            else:
                # Throughput is stable, reset counters
                self.consecutive_increases = 0
                self.consecutive_decreases = 0

        self.last_throughput = current_throughput

    def _increase_concurrency(self) -> None:
        """Increase concurrency level."""
        # Use multiplicative increase with a cap
        if self.current_concurrency < 10:
            self.current_concurrency += 2
        elif self.current_concurrency < 50:
            self.current_concurrency = int(self.current_concurrency * 1.2)
        else:
            self.current_concurrency = int(self.current_concurrency * 1.1)

        self.current_concurrency = min(self.current_concurrency, self.max_concurrency)

    def _decrease_concurrency(self, factor: float = 0.8) -> None:
        """Decrease concurrency level."""
        self.current_concurrency = int(self.current_concurrency * factor)
        self.current_concurrency = max(self.current_concurrency, self.min_concurrency)

    def get_stats(self) -> dict:
        """Get current adaptation statistics."""
        return {
            "current_concurrency": self.current_concurrency,
            "throughput": self.throughput_tracker.get_throughput(),
            "total_completed": self.throughput_tracker.total_completed,
            "total_tasks": self.total_tasks,
            "recent_errors": self.recent_errors,
            "adaptation_history": self.adaptation_history[-10:],  # Last 10 adaptations
        }
