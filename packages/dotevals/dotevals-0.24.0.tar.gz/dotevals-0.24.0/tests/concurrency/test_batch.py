"""Test the batch execution strategy."""

from dotevals.concurrency import Batch


def test_batch_execution():
    """Test that tasks are executed in batches."""
    strategy = Batch(batch_size=3)
    execution_times = []

    def create_tasks():
        for i in range(7):

            def task(task_id=i):
                execution_times.append(task_id)
                return f"result_{task_id}"

            yield task

    results = list(strategy.execute(create_tasks()))

    # Check all tasks executed
    assert len(execution_times) == 7
    assert len(results) == 7
    assert results == [f"result_{i}" for i in range(7)]


def test_batch_with_progress_callback():
    """Test batch execution with progress callback."""
    strategy = Batch(batch_size=2)
    progress_results = []

    def progress_callback(result):
        progress_results.append(result)

    def create_tasks():
        for i in range(5):

            def task(task_id=i):
                return f"result_{task_id}"

            yield task

    results = list(strategy.execute(create_tasks(), progress_callback))

    assert len(results) == 5
    assert len(progress_results) == 5
    assert progress_results == [f"result_{i}" for i in range(5)]
