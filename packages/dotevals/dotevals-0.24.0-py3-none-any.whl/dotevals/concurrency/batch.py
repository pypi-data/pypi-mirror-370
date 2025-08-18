"""Batch execution strategy for sync functions."""

from collections.abc import Callable, Iterator
from typing import TypeVar

T = TypeVar("T")


class Batch:
    """Batch execution strategy for sync functions.

    Groups tasks into batches and executes them sequentially within each batch.
    This is useful for processing large datasets in manageable chunks.
    """

    def __init__(self, batch_size: int = 100):
        """Initialize the batch strategy.

        Args:
            batch_size: Number of tasks to execute in each batch
        """
        self.batch_size = batch_size

    def execute(
        self,
        tasks: Iterator[Callable[[], T]],
        progress_callback: Callable[[T], None] | None = None,
    ) -> Iterator[T]:
        """Execute sync tasks in batches.

        Args:
            tasks: An iterator of callables that return results
            progress_callback: Optional callback to report progress

        Yields:
            Results from executing the tasks
        """
        batch = []
        for task in tasks:
            batch.append(task)
            if len(batch) >= self.batch_size:
                # Execute the batch
                for task_func in batch:
                    result = task_func()
                    if progress_callback:
                        progress_callback(result)
                    yield result
                batch = []

        # Execute remaining tasks in the last batch
        for task_func in batch:
            result = task_func()
            if progress_callback:
                progress_callback(result)
            yield result
