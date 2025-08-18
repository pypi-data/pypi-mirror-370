"""Test the async sequential execution strategy."""

import asyncio

import pytest

from dotevals.concurrency import AsyncSequential


@pytest.mark.asyncio
async def test_async_sequential_execution():
    """Test that async tasks are executed sequentially."""
    strategy = AsyncSequential()
    execution_order = []

    def create_tasks():
        for i in range(3):

            async def task(task_id=i):
                execution_order.append(task_id)
                await asyncio.sleep(0.001)
                return f"result_{task_id}"

            yield task

    results = []
    async for result in strategy.execute(create_tasks()):
        results.append(result)

    # Check execution order is sequential
    assert execution_order == [0, 1, 2]
    assert results == ["result_0", "result_1", "result_2"]


@pytest.mark.asyncio
async def test_async_sequential_with_progress_callback():
    """Test async sequential execution with progress callback."""
    strategy = AsyncSequential()
    progress_results = []

    def progress_callback(result):
        progress_results.append(result)

    def create_tasks():
        for i in range(3):

            async def task(task_id=i):
                await asyncio.sleep(0.001)
                return f"result_{task_id}"

            yield task

    results = []
    async for result in strategy.execute(create_tasks(), progress_callback):
        results.append(result)

    assert results == ["result_0", "result_1", "result_2"]
    assert progress_results == ["result_0", "result_1", "result_2"]


@pytest.mark.asyncio
async def test_async_sequential_without_progress_callback():
    """Test async sequential execution without progress callback."""
    strategy = AsyncSequential()

    def create_tasks():
        for i in range(2):

            async def task(task_id=i):
                await asyncio.sleep(0.001)
                return f"result_{task_id}"

            yield task

    results = []
    async for result in strategy.execute(create_tasks(), None):
        results.append(result)

    assert results == ["result_0", "result_1"]
