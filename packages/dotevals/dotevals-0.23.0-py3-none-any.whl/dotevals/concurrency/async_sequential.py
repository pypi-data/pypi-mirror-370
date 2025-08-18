"""Sequential execution strategy for async functions."""

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import TypeVar

T = TypeVar("T")


class AsyncSequential:
    """Sequential execution for async functions."""

    async def execute(
        self,
        tasks: Iterator[Callable[[], Awaitable[T]]],
        progress_callback: Callable[[T], None] | None = None,
    ) -> AsyncIterator[T]:
        """Execute sync tasks sequentially.

        Args:
            tasks: An iterator of callables that return results
            progress_callback: Optional callback to report progress

        Yields:
            Results from executing the tasks
        """
        for task in tasks:
            result = await task()
            if progress_callback:
                progress_callback(result)
            yield result
