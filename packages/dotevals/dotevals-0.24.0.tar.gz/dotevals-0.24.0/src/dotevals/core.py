import asyncio
import functools
import itertools
from collections.abc import Callable, Coroutine, Generator, Iterable
from typing import (
    Any,
    Optional,
    TypeAlias,
    TypedDict,
    Union,
)

import pytest
from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from dotevals.concurrency import (
    Adaptive,
    AsyncConcurrencyStrategy,
    Sequential,
    SyncConcurrencyStrategy,
)
from dotevals.datasets import _registry
from dotevals.exceptions import InvalidResultError
from dotevals.models import EvaluationSummary, Record, Result, Score
from dotevals.progress import BaseProgressManager, SingleProgress, get_dataset_info
from dotevals.sessions import SessionManager
from dotevals.storage import Storage

# Type aliases for better clarity
ConcurrencyStrategy: TypeAlias = SyncConcurrencyStrategy | AsyncConcurrencyStrategy
ColumnSpec: TypeAlias = str
# DatasetRow can be various formats - tuple, list, dict, or single values
DatasetValue: TypeAlias = str | int | float | bool | None | dict | list
DatasetRow: TypeAlias = (
    tuple[DatasetValue, ...]
    | list[DatasetValue]
    | dict[str, DatasetValue]
    | DatasetValue
)

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # Initial delay in seconds
DEFAULT_MAX_DELAY = 30.0  # Maximum delay between retries


class DatasetInfo(TypedDict, total=False):
    """Type for dataset information dictionary."""

    name: str
    total_rows: int | None


CONNECTION_ERRORS = (
    ConnectionError,
    ConnectionResetError,
    ConnectionAbortedError,
    ConnectionRefusedError,
    TimeoutError,
    OSError,
)


class ForEach:
    def __init__(
        self,
        retries: AsyncRetrying | None = None,
        concurrency: ConcurrencyStrategy | None = None,
    ) -> None:
        """Initialize ForEach decorator with optional configuration.

        Args:
            retries: Optional AsyncRetrying instance for retry configuration
            concurrency: Optional concurrency strategy
        """
        self.retries = retries
        self.concurrency = concurrency

    def __call__(
        self, column_spec: ColumnSpec, dataset: Iterable[DatasetRow]
    ) -> Callable[[Callable], Callable]:
        def core_foreach(
            column_spec: ColumnSpec, dataset: Iterable[DatasetRow]
        ) -> Callable[[Callable], Callable]:
            """
            Decorator that marks a function for running against each item in a dataset.

            When used with `pytest`, the decorated function will be automatically
            executed against all dataset items as part of the evaluation suite.
            Functions decorated by `foreach` can also be executed as normal Python
            functions.

            The decorated function inherits retry, concurrency, and storage configuration
            from the ForEach instance that created it.

            Args:
                column_spec: Comma-separated list of column names
                dataset: An iterator of tuples or lists, each representing a row of data

            Returns:
                A decorated function that can be used as a regular function or as a `pytest` test

            """

            def decorator(
                eval_fn: Callable[..., Result | Any],
            ) -> Callable[
                ..., EvaluationSummary | Coroutine[Any, Any, EvaluationSummary] | Any
            ]:
                if asyncio.iscoroutinefunction(eval_fn):
                    # Create async wrapper for async eval functions
                    @functools.wraps(eval_fn)
                    async def async_wrapper(
                        session_manager: "SessionManager",
                        samples: int | None,
                        progress_manager: BaseProgressManager | None = None,
                        **kwargs: Any,
                    ) -> EvaluationSummary:
                        return await run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset,
                            session_manager,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            progress_manager=progress_manager,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    async_wrapper._column_names = [  # type: ignore
                        col.strip() for col in column_spec.split(",")
                    ]

                    return pytest.mark.dotevals(async_wrapper)
                else:
                    # Create sync wrapper for sync eval functions
                    @functools.wraps(eval_fn)
                    def sync_wrapper(
                        session_manager: "SessionManager",
                        samples: int | None,
                        progress_manager: BaseProgressManager | None = None,
                        **kwargs: Any,
                    ) -> Coroutine[Any, Any, EvaluationSummary]:
                        return run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset,
                            session_manager,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            progress_manager=progress_manager,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    sync_wrapper._column_names = [  # type: ignore
                        col.strip() for col in column_spec.split(",")
                    ]

                    return pytest.mark.dotevals(sync_wrapper)

            return decorator

        return core_foreach(column_spec, dataset)

    def __getattr__(
        self, dataset_name: str
    ) -> Callable[..., Callable[[Callable], Callable]]:
        def dataset_foreach(
            split: str | None = None, **kwargs: Any
        ) -> Callable[[Callable], Callable]:
            dataset_class = _registry.get_dataset_class(dataset_name)
            dataset_instance = (
                dataset_class(split, **kwargs)
                if split is not None
                else dataset_class(**kwargs)
            )
            column_spec = ",".join(dataset_class.columns)

            def decorator(
                eval_fn: Callable[..., Result | Any],
            ) -> Callable[
                ..., EvaluationSummary | Coroutine[Any, Any, EvaluationSummary] | Any
            ]:
                if asyncio.iscoroutinefunction(eval_fn):
                    # Create async wrapper for async eval functions
                    @functools.wraps(eval_fn)
                    async def async_wrapper(
                        session_manager: "SessionManager",
                        samples: int | None,
                        **kwargs: Any,
                    ) -> EvaluationSummary:
                        return await run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset_instance,
                            session_manager,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    async_wrapper._column_names = [  # type: ignore
                        col.strip() for col in column_spec.split(",")
                    ]

                    return pytest.mark.dotevals(async_wrapper)
                else:
                    # Create sync wrapper for sync eval functions
                    @functools.wraps(eval_fn)
                    def sync_wrapper(
                        session_manager: "SessionManager",
                        samples: int | None,
                        **kwargs: Any,
                    ) -> Coroutine[Any, Any, EvaluationSummary]:
                        return run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset_instance,
                            session_manager,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    sync_wrapper._column_names = [  # type: ignore
                        col.strip() for col in column_spec.split(",")
                    ]

                    return pytest.mark.dotevals(sync_wrapper)

            decorator._dataset_name = dataset_name  # type: ignore
            decorator._split = split  # type: ignore
            return decorator

        return dataset_foreach


# Create default instance for usability
foreach = ForEach()


async def run_evaluation(
    eval_fn: Callable[..., Result | Any],
    column_spec: ColumnSpec,
    dataset: Iterable[DatasetRow],
    session_manager: "SessionManager",
    samples: int | None = None,
    retries: AsyncRetrying | None = None,
    concurrency: ConcurrencyStrategy | None = None,
    progress_manager: BaseProgressManager | None = None,
    **kwargs: Any,
) -> EvaluationSummary:
    """
    Run an evaluation function against each item in a dataset.

    Args:
        eval_fn: The function to run for each dataset item
        column_spec: Comma-separated list of column names
        dataset: An iterator of tuples or lists, each representing a row of data
        session_manager: SessionManager instance (handles storage and experiment management, includes evaluation name)
        samples: Maximum number of dataset samples to evaluate (None for all)
        retries: Retry strategy (AsyncRetrying for async, Retrying for sync)
        concurrency: Concurrency strategy (AsyncConcurrencyStrategy or SyncConcurrencyStrategy)
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    session_manager.start_evaluation()

    columns = [col.strip() for col in column_spec.split(",")]

    dataset_info = get_dataset_info(dataset)

    # Type guard: current_evaluation should be set by start_evaluation()
    assert session_manager.current_evaluation is not None, (
        "Evaluation must be started before running"
    )

    completed_items = session_manager.storage.completed_items(
        session_manager.current_experiment, session_manager.current_evaluation
    )
    completed_ids = set(completed_items)

    all_results = session_manager.get_results()
    all_item_ids = {r.item_id for r in all_results}
    items_to_retry = all_item_ids - completed_ids

    # Batch remove from storage all the items that errored out in the
    # previous run since we're going to re-try them.
    if items_to_retry:
        session_manager.storage.remove_error_results_batch(
            session_manager.current_experiment,
            session_manager.current_evaluation,
            list(items_to_retry),
        )

    # Filter the dataset to only keep items that were not completed
    dataset = (
        (item_id, row_data)
        for item_id, row_data in enumerate(dataset)
        if item_id not in completed_ids
    )

    # Limit the dataset to `num_samples` items
    dataset = itertools.islice(dataset, None, samples)

    try:
        if asyncio.iscoroutinefunction(eval_fn):
            # For async functions, pass only AsyncConcurrencyStrategy
            async_concurrency = (
                concurrency
                if concurrency is None or hasattr(concurrency, "execute")
                else None
            )
            result = await _run_evaluation_async(
                eval_fn,
                columns,
                dataset,
                async_concurrency,  # type: ignore
                retries,
                session_manager,
                samples,
                dataset_info,
                progress_manager=progress_manager,
                **kwargs,
            )
        else:
            # For sync functions, pass only SyncConcurrencyStrategy
            sync_concurrency = (
                concurrency
                if concurrency is None or hasattr(concurrency, "execute")
                else None
            )
            result = _run_evaluation_sync(
                eval_fn,
                columns,
                dataset,
                sync_concurrency,  # type: ignore
                retries,
                session_manager,
                samples,
                dataset_info,
                progress_manager=progress_manager,
                **kwargs,
            )

        session_manager.finish_evaluation(success=True)

        return result
    except Exception:
        session_manager.finish_evaluation(success=False)
        raise


def _run_evaluation_sync(
    eval_fn: Callable,
    columns: list[str],
    dataset: Iterable,
    concurrency: SyncConcurrencyStrategy | None,
    retries: Retrying | None,
    session_manager: "SessionManager",
    samples: int | None,
    dataset_info: DatasetInfo,
    progress_manager: BaseProgressManager | None = None,
    **kwargs: Any,
) -> EvaluationSummary:
    """
    Run the evaluation when `eval_fn` is a Python function, against
    each item in the dataset.

    Args:
        eval_fn: The function to run for each dataset item
        columns: list of column names that map to dataset fields
        dataset: An iterator of tuples or lists, each representing a row of data
        concurrency: Concurrency strategy for sync execution (defaults to Sequential())
        retries: Retry strategy for handling failures (defaults to Retrying with 3 attempts)
        samples: Maximum number of samples to evaluate
        dataset_info: Optional dataset information (name, split, size)
        session_manager: The current session's session manager (includes evaluation name)
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    if concurrency is None:
        concurrency = Sequential()

    if retries is None:
        retries = Retrying(
            retry=retry_if_exception_type(CONNECTION_ERRORS),
            stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
            wait=wait_exponential_jitter(
                initial=DEFAULT_RETRY_DELAY, max=DEFAULT_MAX_DELAY
            ),
            reraise=True,
        )

    # When the library is used programmatically we automatically instantiate the
    # `SingleProgress` otherwise we use the one provided by the pytest runner.
    if progress_manager is None:
        progress_manager = SingleProgress()

    # Type guard: current_evaluation should be set by run_evaluation()
    assert session_manager.current_evaluation is not None, (
        "Evaluation must be started before running"
    )

    def create_tasks() -> Generator[Callable[[], Record], None, None]:
        """Create an iterator over evaluation tasks."""
        for item_id, row_data in dataset:
            row_dict = _format_data(row_data, columns)

            def task(
                item_id: int = item_id, row_dict: dict[str, DatasetValue] = row_dict
            ) -> Record:
                try:
                    wrapped_fn = retries.wraps(eval_fn) if retries else eval_fn
                    result = wrapped_fn(**row_dict, **kwargs)

                    # Auto-wrap Score objects into Result
                    if isinstance(result, Score):
                        result = Result(result)
                    elif not isinstance(result, Result):
                        raise InvalidResultError(eval_fn.__name__, type(result))

                    # If the Result contains an error we propagate it to Record.
                    #
                    # A result can contain an error when it is specified by the
                    # user. For instance if we expect a result to be valid JSON,
                    # we would parse it between try/except and return a `Record`
                    # with the error in case the parsing fails.
                    if result.error is not None:
                        return Record(result, item_id, row_dict, result.error)
                    else:
                        return Record(result, item_id, row_dict)
                except Exception as e:
                    error_result = Result(prompt="")
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    return Record(error_result, item_id, row_dict, error_msg)

            yield task

    # Run the evaluation.
    #
    # When the library is used programmatically we automatically instantiate the
    # `ProgressManager` otherwise we use the one provided by the pytest runner.
    with progress_manager:
        dataset_size = dataset_info.get("total_rows")
        progress_manager.start_evaluation(
            session_manager.current_evaluation, dataset_size
        )

        # Capture evaluation name for closure
        evaluation_name = session_manager.current_evaluation

        def progress_callback(result: Record) -> None:
            progress_manager.update_evaluation_progress(evaluation_name, result=result)

        for result in concurrency.execute(create_tasks(), progress_callback):
            session_manager.add_results([result])

    results = session_manager.get_results()

    return EvaluationSummary(results)


async def _run_evaluation_async(
    eval_fn: Callable,
    columns: list[str],
    dataset: Iterable,
    concurrency: AsyncConcurrencyStrategy | None,
    retries: AsyncRetrying | None,
    session_manager: "SessionManager",
    samples: int | None,
    dataset_info: DatasetInfo,
    progress_manager: BaseProgressManager | None = None,
    **kwargs: Any,
) -> EvaluationSummary:
    """
    Run the evaluation when `eval_fn` is a coroutine, against each item in the
    dataset.

    Args:
        eval_fn: The function to run for each dataset item
        columns: list of column names that map to dataset fields
        dataset: An iterator of tuples or lists, each representing a row of data
        concurrency: Concurrency strategy for async execution (defaults to SlidingWindowStrategy)
        retries: Retry strategy for handling failures (defaults to AsyncRetrying with connection error handling)
        samples: Maximum number of samples to evaluate
        dataset_info: Optional dataset information (name, split, size)
        session_manager: The current session's session manager (includes evaluation name)
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    if concurrency is None:
        concurrency = Adaptive()

    if retries is None:
        retries = AsyncRetrying(
            retry=retry_if_exception_type(CONNECTION_ERRORS),
            stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
            wait=wait_exponential_jitter(
                initial=DEFAULT_RETRY_DELAY, max=DEFAULT_MAX_DELAY
            ),
        )

    # When the library is used programmatically we automatically instantiate the
    # `SingleProgress` otherwise we use the one provided by the pytest runner.
    if progress_manager is None:
        progress_manager = SingleProgress()

    # Type guard: current_evaluation should be set by run_evaluation()
    assert session_manager.current_evaluation is not None, (
        "Evaluation must be started before running"
    )

    def create_tasks() -> Generator[Callable[[], Any], None, None]:
        """Create an async iterator of evaluation tasks."""
        for item_id, row_data in dataset:
            row_dict = _format_data(row_data, columns)

            async def task(
                item_id: int = item_id, row_dict: dict[str, DatasetValue] = row_dict
            ) -> Record:
                try:
                    wrapped_fn = retries.wraps(eval_fn) if retries else eval_fn
                    result = await wrapped_fn(**row_dict, **kwargs)

                    # Auto-wrap Score objects into Result
                    if isinstance(result, Score):
                        result = Result(result)
                    elif not isinstance(result, Result):
                        raise InvalidResultError(eval_fn.__name__, type(result))

                    # If the Result contains an error we propagate it to Record.
                    #
                    # A result can contain an error when it is specified by the
                    # user. For instance if we expect a result to be valid JSON,
                    # we would parse it between try/except and return a `Record`
                    # with the error in case the parsing fails.
                    if result.error is not None:
                        return Record(result, item_id, row_dict, result.error)
                    else:
                        return Record(result, item_id, row_dict)
                except Exception as e:
                    # Create empty Result for error cases
                    empty_result = Result(prompt="")
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    return Record(empty_result, item_id, row_dict, error_msg)

            yield task

    # Run the evaluation
    with progress_manager:
        dataset_size = dataset_info.get("total_rows")
        progress_manager.start_evaluation(
            session_manager.current_evaluation, dataset_size
        )

        # Capture evaluation name for closure
        evaluation_name = session_manager.current_evaluation

        def progress_callback(result: Record) -> None:
            progress_manager.update_evaluation_progress(evaluation_name, result=result)

        async for result in concurrency.execute(create_tasks(), progress_callback):
            session_manager.add_results([result])

    results = session_manager.get_results()

    return EvaluationSummary(results)


def _format_data(row_data: DatasetRow, columns: list[str]) -> dict[str, DatasetValue]:
    """Handle different data formats for the datasets."""
    if len(columns) == 1 and not (
        isinstance(row_data, (tuple | list)) and len(row_data) == 1
    ):
        # Single column with non-tuple data: pass the data item directly
        # (handles dicts, objects, etc.)
        # Cast is safe here since row_data is DatasetRow which can be DatasetValue
        return {columns[0]: row_data}  # type: ignore[dict-item]
    else:
        # Multiple columns OR single column with single-element tuple: use zip logic
        # Cast is safe since we checked row_data is tuple/list
        return dict(zip(columns, row_data))  # type: ignore[arg-type]
