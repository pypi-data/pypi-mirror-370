"""Sliding window concurrency strategy for async functions."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from typing import TypeVar

T = TypeVar("T")


class SlidingWindow:
    """Sliding window implementation for async concurrency."""

    def __init__(self, max_concurrency: int = 10):
        """Initialize the sliding window strategy.

        Args:
            max_concurrency: Maximum number of concurrent tasks
        """
        self.max_concurrency = max_concurrency

    async def execute(
        self,
        tasks: Iterator[Callable[[], T]],
        progress_callback: Callable[[T], None] | None = None,
    ) -> AsyncIterator[T]:
        """Execute tasks with sliding window concurrency control.

        This maintains a sliding window of concurrent tasks, keeping up to
        max_concurrency tasks running at all times.

        Args:
            tasks: An iterator of callables that return awaitable results
            progress_callback: Optional callback to report progress

        Yields:
            Results from executing the tasks
        """
        tasks_iter = iter(tasks)
        pending_tasks = set()

        try:
            # Fill the initial window to max_concurrency
            for _ in range(self.max_concurrency):
                try:
                    task_func = next(tasks_iter)
                    task: asyncio.Task = asyncio.create_task(task_func())  # type: ignore
                    pending_tasks.add(task)
                except StopIteration:
                    break

            # Process tasks as they complete
            while pending_tasks:
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for completed_task in done:
                    result = await completed_task
                    if progress_callback:
                        progress_callback(result)
                    yield result

                # For each completed task, try to add a new one
                for _ in range(len(done)):
                    try:
                        task_func = next(tasks_iter)
                        task = asyncio.create_task(task_func())  # type: ignore
                        pending_tasks.add(task)
                    except StopIteration:
                        break

        except Exception:
            for task in pending_tasks:
                task.cancel()
            raise
