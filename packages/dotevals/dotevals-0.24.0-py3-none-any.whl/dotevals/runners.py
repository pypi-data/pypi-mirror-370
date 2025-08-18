"""Execution runners for dotevals evaluations."""

import asyncio
from typing import Any, Optional

import pytest

from dotevals.progress import MultiProgress


class Runner:
    """Base runner for dotevals evaluations.

    The Runner class handles all evaluation orchestration including:
    - Sequential and concurrent execution strategies
    - Fixture lifecycle management
    - Progress tracking and reporting
    - Result collection

    For resource management (model clients, database connections, etc.), use
    ModelProvider plugins distributed as pytest fixtures.

    Examples:
        Direct usage:
        ```python
        runner = Runner(
            experiment_name="my_experiment",
            samples=100,
            concurrent=True
        )
        await runner.run_evaluations(evaluation_items)
        ```

        The Runner handles all orchestration logic internally, so subclasses
        typically don't need to override any methods.
    """

    def __init__(
        self,
        experiment_name: str | None = None,
        samples: int | None = None,
        storage: str | None = None,
        concurrent: bool = True,
        results_dict: dict[str, Any] | None = None,
    ) -> None:
        """Initialize runner with evaluation parameters.

        Args:
            experiment_name: Name of the experiment
            samples: Number of samples to evaluate
            storage: Storage backend path (e.g., 'json://.dotevals', 'sqlite://results.db')
            concurrent: Whether to run async evaluations concurrently
            results_dict: Optional dictionary to store evaluation results
        """
        self.experiment_name = experiment_name
        self.samples = samples
        self.storage = storage
        self.concurrent = concurrent
        self.results = results_dict if results_dict is not None else {}
        self.progress_manager = MultiProgress()

    async def run_evaluations(self, evaluation_items: list[pytest.Item]) -> None:
        """Run all evaluation items with common orchestration logic.

        This method provides the standard orchestration for running evaluations,
        handling both sequential and concurrent execution.

        Args:
            evaluation_items: List of pytest items representing evaluations
        """
        if not evaluation_items:
            return

        # Separate items by execution strategy
        sequential_items = []
        concurrent_items = []

        for item in evaluation_items:
            if self.concurrent and _is_async_evaluation(item):
                concurrent_items.append(item)
            else:
                sequential_items.append(item)

        # Start progress display
        total_items = len(sequential_items) + len(concurrent_items)
        self.progress_manager.start(total_items)

        try:
            # Run sequential items first
            for item in sequential_items:
                await self._run_single_evaluation(item)

            # Run concurrent items together
            if concurrent_items:
                tasks = []
                for item in concurrent_items:
                    task = asyncio.create_task(self._run_single_evaluation(item))
                    tasks.append(task)
                await asyncio.gather(*tasks)
        finally:
            self.progress_manager.finish()

    async def _run_single_evaluation(self, item: pytest.Item) -> None:
        """Execute a single evaluation item with fixture management.

        This method handles the execution of individual evaluations, including
        creating fixtures before and tearing them down after the evaluation,
        properly handling both sync and async functions.

        Args:
            item: The pytest Item representing a single evaluation
        """
        from dotevals.fixtures import FixtureManager
        from dotevals.sessions import SessionManager

        eval_fn = item.function

        # Create SessionManager for this evaluation
        session_manager = SessionManager(
            evaluation_name=item.name,
            experiment_name=self.experiment_name,
            storage=self.storage,
        )

        # Create fixtures for this evaluation. They will be torn down
        # after the evaluation has run.
        fixture_kwargs, request = await FixtureManager.create_fixtures(item)

        try:
            if asyncio.iscoroutinefunction(eval_fn):
                result = await eval_fn(
                    session_manager=session_manager,
                    samples=self.samples,
                    progress_manager=self.progress_manager,
                    **fixture_kwargs,
                )
            else:
                result = eval_fn(
                    session_manager=session_manager,
                    samples=self.samples,
                    progress_manager=self.progress_manager,
                    **fixture_kwargs,
                )
                if asyncio.iscoroutine(result):
                    result = await result

            self.results[item.name] = result
        finally:
            await FixtureManager.teardown_fixtures(request)


def _is_async_evaluation(item: pytest.Item) -> bool:
    """Check if an evaluation item is async."""
    eval_fn = item.function
    original_func = getattr(eval_fn, "__wrapped__", eval_fn)
    return asyncio.iscoroutinefunction(original_func)
