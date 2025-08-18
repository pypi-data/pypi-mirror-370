"""Interactive API for running evaluations."""

import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional

from dotevals.core import run_evaluation
from dotevals.models import EvaluationSummary, Record
from dotevals.progress import SingleProgress
from dotevals.sessions import SessionManager
from dotevals.storage import Storage, registry


def run(
    eval_fn: Callable,
    experiment: str | None = None,
    samples: int | None = None,
    storage: Storage | str | None = None,
    **kwargs,
) -> "Results":
    """
    Run a decorated evaluation function and return a Results object.

    The evaluation function must be decorated with @foreach.

    Args:
        eval_fn: Evaluation function decorated with @foreach
        experiment: Experiment name (auto-generated if None)
        limit: Limit number of samples
        storage: Storage backend (defaults to json://.dotevals)
        **kwargs: Additional arguments for the evaluation function

    Returns:
        Results object with access to the data

    Example:
        @foreach("question,answer", dataset)
        def eval_math(question, answer, model):
            result = model.generate(question)
            return exact_match(result, answer)

        results = run(eval_math, model=my_model)
        print(results.summary())
    """
    # Check if function is decorated with @foreach
    if not hasattr(eval_fn, "pytestmark"):
        raise ValueError(
            "The evaluation function must be decorated with @foreach. "
            "Example: @foreach('col1,col2', dataset)"
        )

    # Setup storage
    if storage is None:
        storage = registry.get_storage("json://.dotevals")
    elif isinstance(storage, str):
        storage = registry.get_storage(storage)

    # Auto-generate experiment name
    if experiment is None:
        experiment = f"run_{datetime.now():%Y%m%d_%H%M%S}"

    # Get evaluation name from function
    evaluation_name = eval_fn.__name__

    # Create session manager
    session_manager = SessionManager(
        evaluation_name=evaluation_name, experiment_name=experiment, storage=storage
    )

    # Use SingleProgress for notebook display
    progress_manager = SingleProgress()

    coro = eval_fn(
        session_manager=session_manager,
        samples=samples,
        progress_manager=progress_manager,
        **kwargs,
    )

    # Run the evaluation
    asyncio.run(coro)

    # Return Results object pointing to this specific run
    return Results(storage=storage, experiment=experiment, evaluation=evaluation_name)


class Results:
    """Results from a specific evaluation run."""

    def __init__(self, storage: Storage, experiment: str, evaluation: str):
        self.storage = storage
        self.experiment = experiment
        self.evaluation = evaluation
        self._records: list[Record] | None = None

    @property
    def records(self) -> list[Record]:
        """Lazy load records from storage."""
        if self._records is None:
            self._records = self.storage.get_results(self.experiment, self.evaluation)
        return self._records

    def summary(self) -> dict[str, Any]:
        """Get evaluation summary metrics."""
        # Create evaluation summary
        eval_summary = EvaluationSummary(self.records)

        # Count errors
        error_count = sum(1 for r in self.records if r.error is not None)

        return {
            "total": len(self.records),
            "errors": error_count,
            "metrics": eval_summary.summary,
        }
