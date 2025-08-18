"""Tests for the runner system."""

import asyncio
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from dotevals import foreach
from dotevals.evaluators import exact_match
from dotevals.models import Result
from dotevals.runners import Runner, _is_async_evaluation
from dotevals.sessions import SessionManager


# Helper to create async mock for FixtureManager
def create_async_fixture_manager_mock(fixture_values=None, mock_request=None):
    """Create an async mock for FixtureManager."""
    if fixture_values is None:
        fixture_values = {}
    if mock_request is None:
        mock_request = MagicMock()

    mock_fm = MagicMock()

    async def async_create_fixtures(item):
        return fixture_values, mock_request

    async def async_teardown_fixtures(request):
        return None

    mock_fm.create_fixtures = async_create_fixtures
    mock_fm.teardown_fixtures = async_teardown_fixtures

    return mock_fm


class TestRunner:
    """Tests for the Runner class."""

    @pytest.fixture
    def results_dict(self):
        """Create a results dictionary."""
        return {}

    @pytest.fixture
    def runner(self, results_dict):
        """Create a Runner instance."""
        return Runner(
            experiment_name="test_exp",
            samples=10,
            concurrent=False,
            results_dict=results_dict,
        )

    @pytest.mark.asyncio
    async def test_run_empty_evaluations(self, runner):
        """Test running with empty evaluation list."""
        await runner.run_evaluations([])
        # Should not raise

    @pytest.mark.asyncio
    async def test_run_sync_evaluation(self, runner, results_dict):
        """Test running a synchronous evaluation."""
        # Create a mock item
        mock_item = MagicMock()
        mock_item.name = "test_eval"
        mock_item.fixtures = {"model": "test_model"}

        # Create a sync evaluation function
        def sync_eval(session_manager, samples, progress_manager, **kwargs):
            return {"success": True, "model": kwargs.get("model")}

        mock_item.function = sync_eval

        # Mock FixtureManager to return our fixture values
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock(
            {"model": "test_model"},
            mock_request,
        )

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Run evaluation
            await runner.run_evaluations([mock_item])

        # Check result was stored
        assert "test_eval" in results_dict
        assert results_dict["test_eval"]["success"] is True
        assert results_dict["test_eval"]["model"] == "test_model"

    @pytest.mark.asyncio
    async def test_run_async_evaluation(self, runner, results_dict):
        """Test running an asynchronous evaluation."""
        # Create a mock item
        mock_item = MagicMock()
        mock_item.name = "test_async_eval"
        mock_item.fixtures = {"model": "test_model"}

        # Create an async evaluation function
        async def async_eval(session_manager, samples, progress_manager, **kwargs):
            await asyncio.sleep(0.01)  # Simulate async work
            return {"success": True, "async": True}

        mock_item.function = async_eval

        # Mock FixtureManager to return our fixture values
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock(
            {"model": "test_model"},
            mock_request,
        )

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Run evaluation
            await runner.run_evaluations([mock_item])

        # Check result was stored
        assert "test_async_eval" in results_dict
        assert results_dict["test_async_eval"]["success"] is True
        assert results_dict["test_async_eval"]["async"] is True

    @pytest.mark.asyncio
    async def test_run_mixed_evaluations_sequential(self, runner, results_dict):
        """Test running mixed sync/async evaluations sequentially."""
        # Runner fixture already has concurrent=False

        # Create mock items
        sync_item = MagicMock()
        sync_item.name = "sync_eval"
        sync_item.fixtures = {}
        sync_item.function = lambda **kwargs: {"type": "sync"}

        async_item = MagicMock()
        async_item.name = "async_eval"
        async_item.fixtures = {}

        async def async_fn(**kwargs):
            return {"type": "async"}

        async_item.function = async_fn

        # Mock FixtureManager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Run evaluations
            await runner.run_evaluations([sync_item, async_item])

        # Check both results
        assert results_dict["sync_eval"]["type"] == "sync"
        assert results_dict["async_eval"]["type"] == "async"

    @pytest.mark.asyncio
    async def test_run_concurrent_evaluations(self, results_dict):
        """Test running async evaluations concurrently."""
        # Create a runner with concurrent=True
        concurrent_runner = Runner(
            experiment_name="test_exp",
            samples=10,
            concurrent=True,
            results_dict=results_dict,
        )

        # Track execution order
        execution_order = []

        def make_async_eval(name, delay):
            async def async_eval(**kwargs):
                execution_order.append(f"{name}_start")
                await asyncio.sleep(delay)
                execution_order.append(f"{name}_end")
                return {"name": name}

            return async_eval

        # Create async items with different delays
        item1 = MagicMock()
        item1.name = "eval1"
        item1.fixtures = {}
        item1.function = make_async_eval("eval1", 0.02)

        item2 = MagicMock()
        item2.name = "eval2"
        item2.fixtures = {}
        item2.function = make_async_eval("eval2", 0.01)

        # Mock FixtureManager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Run evaluations
            await concurrent_runner.run_evaluations([item1, item2])

        # Check that they ran concurrently (eval2 should finish before eval1)
        assert execution_order == [
            "eval1_start",
            "eval2_start",
            "eval2_end",
            "eval1_end",
        ]
        assert results_dict["eval1"]["name"] == "eval1"
        assert results_dict["eval2"]["name"] == "eval2"

    @pytest.mark.asyncio
    async def test_run_real_evaluation_function(self):
        """Test running a real evaluation function without mocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create real dataset
            test_data = [("apple", "apple"), ("banana", "banana"), ("cherry", "orange")]

            # Create real evaluation function
            @foreach("text,expected", test_data)
            def real_eval(text, expected):
                return Result(exact_match(text, expected))

            # Create real session manager
            import uuid

            unique_id = str(uuid.uuid4())[:8]
            session_manager = SessionManager(
                experiment_name=f"test_real_{unique_id}",
                evaluation_name=f"eval_real_{unique_id}",
                storage=f"json://{tmpdir}",
            )

            # Run evaluation
            summary = await real_eval(session_manager, samples=None)

            # Verify results
            assert len(summary.results) == 3
            assert (
                summary.summary["exact_match"]["accuracy"] == 2 / 3
            )  # 2 matches out of 3

    @pytest.mark.asyncio
    async def test_run_real_async_evaluation(self):
        """Test running a real async evaluation function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create real dataset
            test_data = [(1, 1), (2, 4), (3, 9)]

            # Create real async evaluation function
            @foreach("num,expected", test_data)
            async def real_async_eval(num, expected):
                await asyncio.sleep(0.001)  # Simulate async work
                result = num * num
                return Result(exact_match(result, expected))

            # Create real session manager
            import uuid

            unique_id = str(uuid.uuid4())[:8]
            session_manager = SessionManager(
                experiment_name=f"test_async_{unique_id}",
                evaluation_name=f"eval_async_{unique_id}",
                storage=f"json://{tmpdir}",
            )

            # Run evaluation
            summary = await real_async_eval(session_manager, samples=None)

            # Verify results
            assert len(summary.results) == 3
            assert (
                summary.summary["exact_match"]["accuracy"] == 1.0
            )  # All squares match

    @pytest.mark.asyncio
    async def test_run_real_evaluation_with_errors(self):
        """Test running a real evaluation that has some errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create real dataset
            test_data = [("valid1", "ok"), ("error", "fail"), ("valid2", "ok")]

            # Create evaluation function that raises errors
            @foreach("input,expected", test_data)
            def eval_with_errors(input, expected):
                if input == "error":
                    raise ValueError("Intentional error for testing")
                return Result(exact_match(expected, "ok"))

            # Create real session manager
            import uuid

            unique_id = str(uuid.uuid4())[:8]
            session_manager = SessionManager(
                experiment_name=f"test_errors_{unique_id}",
                evaluation_name=f"eval_errors_{unique_id}",
                storage=f"json://{tmpdir}",
            )

            # Run evaluation - should handle errors gracefully
            summary = await eval_with_errors(session_manager, samples=None)

            # Verify results
            assert len(summary.results) == 3
            # Check we have 2 successes and 1 error
            errors = [r for r in summary.results if r.error is not None]
            successes = [r for r in summary.results if r.error is None]
            assert len(errors) == 1
            assert len(successes) == 2
            assert "ValueError" in errors[0].error


class TestRunnerEdgeCases:
    """Edge case tests for Runner."""

    @pytest.mark.asyncio
    async def test_runner_with_fixture_kwargs_error(self):
        """Test Runner when fixture kwargs are missing."""
        results_dict = {}
        runner = Runner(results_dict=results_dict)

        # Create item without fixtures
        mock_item = MagicMock()
        mock_item.name = "test"
        del mock_item.fixtures  # Remove the attribute
        mock_item.function = lambda **kwargs: {"result": "ok"}

        # Mock FixtureManager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Should still work, using empty dict
            await runner.run_evaluations([mock_item])

        assert "test" in results_dict
        assert results_dict["test"]["result"] == "ok"

    @pytest.mark.asyncio
    async def test_runner_progress_manager(self):
        """Test Runner progress manager functionality."""
        results = {}
        runner = Runner(results_dict=results)

        # Verify progress manager is created
        assert hasattr(runner, "progress_manager")

        # Create multiple items to test progress
        items = []
        for i in range(3):
            item = MagicMock()
            item.name = f"test_{i}"
            item.fixtures = {}
            item.function = lambda **kwargs: {"id": f"test_{i}"}
            items.append(item)

        # Mock FixtureManager and progress manager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            with patch.object(runner.progress_manager, "start") as mock_start:
                with patch.object(runner.progress_manager, "finish") as mock_finish:
                    await runner.run_evaluations(items)

                    # Verify progress tracking
                    mock_start.assert_called_once_with(3)
                    mock_finish.assert_called_once()


class TestRunnerConcurrentTasks:
    """Test Runner concurrent task handling."""

    @pytest.mark.asyncio
    async def test_concurrent_task_creation(self):
        """Test concurrent task creation code path."""
        results = {}
        runner = Runner(concurrent=True, results_dict=results)

        # Create async items
        async def eval1(**kwargs):
            await asyncio.sleep(0.01)
            return {"name": "eval1"}

        async def eval2(**kwargs):
            await asyncio.sleep(0.01)
            return {"name": "eval2"}

        item1 = MagicMock()
        item1.name = "eval1"
        item1.fixtures = {}
        item1.function = eval1

        item2 = MagicMock()
        item2.name = "eval2"
        item2.fixtures = {}
        item2.function = eval2

        # Mock FixtureManager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Spy on asyncio to verify task creation
            with patch("asyncio.create_task", wraps=asyncio.create_task) as mock_create:
                await runner.run_evaluations([item1, item2])

                # Verify tasks were created
                assert mock_create.call_count == 2

        # Verify results
        assert results["eval1"]["name"] == "eval1"
        assert results["eval2"]["name"] == "eval2"


class TestRunnerUtilities:
    """Tests for runner utility functions."""

    def test_is_async_evaluation(self):
        """Test _is_async_evaluation function."""
        # Test sync function
        sync_item = MagicMock()
        sync_item.function = lambda: None
        assert not _is_async_evaluation(sync_item)

        # Test async function
        async_item = MagicMock()

        async def async_fn():
            pass

        async_item.function = async_fn
        assert _is_async_evaluation(async_item)

        # Test wrapped function
        wrapped_item = MagicMock()
        wrapped_fn = MagicMock()
        wrapped_fn.__wrapped__ = async_fn
        wrapped_item.function = wrapped_fn
        assert _is_async_evaluation(wrapped_item)

    def test_is_async_evaluation_edge_cases(self):
        """Test _is_async_evaluation with various edge cases."""
        # Test with object that has no function attribute
        item = MagicMock()
        del item.function  # Remove function attribute
        with pytest.raises(AttributeError):
            _is_async_evaluation(item)


class TestProgressManager:
    """Test progress manager integration."""

    @pytest.mark.asyncio
    async def test_empty_evaluation_list_progress(self):
        """Test that progress manager handles empty evaluation list."""
        runner = Runner()

        # Spy on progress manager
        with patch.object(runner.progress_manager, "start") as mock_start:
            with patch.object(runner.progress_manager, "finish") as mock_finish:
                # Run with empty list
                await runner.run_evaluations([])

                # Progress manager should not be called for empty list
                mock_start.assert_not_called()
                mock_finish.assert_not_called()


class TestRunnerIntegration:
    """Integration tests for the runner system."""

    @pytest.mark.asyncio
    async def test_runner_initialization(self):
        """Test Runner initialization with parameters."""
        runner = Runner(experiment_name="exp1", samples=10, concurrent=False)
        assert runner.experiment_name == "exp1"
        assert runner.samples == 10
        assert runner.concurrent is False

        # Test with defaults
        runner2 = Runner()
        assert runner2.experiment_name is None
        assert runner2.samples is None
        assert runner2.concurrent is True

    @pytest.mark.asyncio
    async def test_sync_function_returns_coroutine(self):
        """Test that a sync function returning a coroutine is handled correctly."""
        results = {}
        runner = Runner(results_dict=results)

        # Create a sync function that returns a coroutine
        async def async_result():
            await asyncio.sleep(0.01)
            return {"result": "from_coroutine"}

        def sync_func_returning_coroutine(**kwargs):
            # This sync function returns a coroutine object
            return async_result()

        # Create mock item
        item = MagicMock()
        item.name = "test_eval"
        item.function = sync_func_returning_coroutine
        item.fixtures = {}

        # Mock FixtureManager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Run the evaluation
            await runner.run_evaluations([item])

        # Verify the coroutine was awaited and result stored
        assert "test_eval" in results
        assert results["test_eval"]["result"] == "from_coroutine"

    @pytest.mark.asyncio
    async def test_runner_exception_handling(self):
        """Test runner handles exceptions during evaluation."""
        runner = Runner()
        results = {}
        runner.results = results

        # Create mock item
        mock_item = MagicMock()
        mock_item.name = "test_eval"

        # Create function that raises exception
        def failing_eval(session_manager, samples, progress_manager, **kwargs):
            raise ValueError("Test error")

        mock_item.function = failing_eval

        # Mock fixture manager
        mock_request = MagicMock()
        mock_fm = create_async_fixture_manager_mock({}, mock_request)

        with patch("dotevals.fixtures.FixtureManager", mock_fm):
            # Should raise the exception
            with pytest.raises(ValueError, match="Test error"):
                await runner._run_single_evaluation(mock_item)

            # Note: We can't easily verify teardown was called with the current mock setup
            # but the test verifies the exception propagates correctly

    def test_runner_default_initialization(self):
        """Test runner initialization with defaults."""
        runner = Runner()

        assert runner.experiment_name is None
        assert runner.samples is None
        assert runner.concurrent is True  # Default value
        assert runner.results == {}
        assert runner.progress_manager is not None
