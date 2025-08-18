"""Test the sequential execution strategy."""

import pytest

from dotevals.concurrency import Sequential


def test_sequential_execution():
    """Test that tasks are executed sequentially."""
    strategy = Sequential()
    execution_order = []

    def create_tasks():
        for i in range(5):

            def task(task_id=i):
                execution_order.append(task_id)
                return f"result_{task_id}"

            yield task

    results = list(strategy.execute(create_tasks()))

    # Check execution order is sequential
    assert execution_order == [0, 1, 2, 3, 4]
    assert results == ["result_0", "result_1", "result_2", "result_3", "result_4"]


def test_sequential_with_progress_callback():
    """Test sequential execution with progress callback."""
    strategy = Sequential()
    progress_results = []

    def progress_callback(result):
        progress_results.append(result)

    def create_tasks():
        for i in range(3):

            def task(task_id=i):
                return f"result_{task_id}"

            yield task

    results = list(strategy.execute(create_tasks(), progress_callback))

    assert results == ["result_0", "result_1", "result_2"]
    assert progress_results == ["result_0", "result_1", "result_2"]


def test_sequential_with_exception():
    """Test that exceptions are propagated."""
    strategy = Sequential()

    def create_tasks():
        yield lambda: "result_0"
        yield lambda: (_ for _ in ()).throw(ValueError("test error"))
        yield lambda: "result_2"

    results = []
    with pytest.raises(ValueError, match="test error"):
        for result in strategy.execute(create_tasks()):
            results.append(result)

    # Only the first task should have completed
    assert results == ["result_0"]
