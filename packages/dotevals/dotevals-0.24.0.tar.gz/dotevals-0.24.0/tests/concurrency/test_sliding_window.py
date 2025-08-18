"""Test the sliding window async execution strategy."""

import asyncio

import pytest

from dotevals.concurrency import SlidingWindow


@pytest.mark.asyncio
async def test_sliding_window_execution():
    """Test that tasks are executed with concurrency control."""
    strategy = SlidingWindow(max_concurrency=2)
    currently_running = 0
    max_concurrent = 0

    def create_tasks():
        for i in range(5):

            async def task(task_id=i):
                nonlocal currently_running, max_concurrent
                currently_running += 1
                max_concurrent = max(max_concurrent, currently_running)
                await asyncio.sleep(0.01)  # Simulate work
                currently_running -= 1
                return f"result_{task_id}"

            yield task

    results = []
    async for result in strategy.execute(create_tasks()):
        results.append(result)

    # Check all tasks completed
    assert len(results) == 5
    assert all(r.startswith("result_") for r in results)
    # Check concurrency was limited
    assert max_concurrent <= 2


@pytest.mark.asyncio
async def test_sliding_window_with_progress_callback():
    """Test sliding window execution with progress callback."""
    strategy = SlidingWindow(max_concurrency=3)
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


@pytest.mark.asyncio
async def test_sliding_window_with_exception():
    """Test that exceptions in tasks are propagated."""
    strategy = SlidingWindow(max_concurrency=2)

    def create_tasks():
        async def task1():
            await asyncio.sleep(0.01)
            return "result_1"

        async def task2():
            await asyncio.sleep(0.005)
            raise ValueError("test error")

        async def task3():
            return "result_3"

        yield task1
        yield task2
        yield task3

    results = []

    with pytest.raises(ValueError, match="test error"):
        async for result in strategy.execute(create_tasks()):
            results.append(result)

    # The strategy executes tasks concurrently, so we might get some results
    # before the exception is raised
    assert len(results) <= 3  # At most all results if exception is last
