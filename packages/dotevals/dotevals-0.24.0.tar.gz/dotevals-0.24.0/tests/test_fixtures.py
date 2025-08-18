"""Tests for the fixtures module."""

import asyncio
from unittest.mock import MagicMock, Mock

import pytest
from _pytest.fixtures import FixtureDef

from dotevals.fixtures import (
    DeferredFixtureRequest,
    FixtureManager,
    create_mock_request,
    handle_async_generator_fixture,
    handle_sync_generator_fixture,
    resolve_fixture_dependencies,
)


def create_mock_fixture_manager(fixture_defs):
    """Helper to create a mock fixture manager with getfixturedefs support."""
    mock_fm = MagicMock()

    def mock_getfixturedefs(name, item):
        # Return the fixture defs if we have them
        if name in fixture_defs:
            return fixture_defs[name]
        return None

    mock_fm.getfixturedefs.side_effect = mock_getfixturedefs
    # Keep _arg2fixturedefs for any tests that might still use it
    mock_fm._arg2fixturedefs = fixture_defs

    return mock_fm


class TestDeferredFixtureRequest:
    """Tests for DeferredFixtureRequest class."""

    def test_init_with_fixture_manager(self):
        """Test initialization with fixture manager."""
        mock_item = MagicMock()
        mock_session = MagicMock()

        mock_fixture_def = MagicMock(spec=FixtureDef)
        mock_fm = create_mock_fixture_manager(
            {
                "fixture1": [mock_fixture_def],
                "fixture2": [mock_fixture_def, mock_fixture_def],
            }
        )

        mock_session._fixturemanager = mock_fm
        mock_item.session = mock_session

        request = DeferredFixtureRequest(mock_item)

        assert request.item is mock_item
        assert request._fixture_manager is mock_fm
        # We no longer pre-load fixture defs, they're resolved on-demand

    def test_init_without_fixture_manager(self):
        """Test initialization without fixture manager."""
        mock_item = MagicMock()
        del mock_item.session

        request = DeferredFixtureRequest(mock_item)

        assert request.item is mock_item
        assert request._fixture_manager is None
        assert request._fixture_values == {}
        assert request._finalizers == []


class TestFixtureHelpers:
    """Tests for helper functions that still exist."""

    def test_create_mock_request_with_param(self):
        """Test creating mock request with a parameter value."""
        parent = Mock()
        parent.item = Mock(name="test_item")

        param_value = {"key": "value"}
        mock_req = create_mock_request(param_value, parent)

        assert mock_req.param == param_value
        assert mock_req.item == parent.item
        assert mock_req.node == parent.item

    def test_create_mock_request_with_none_param(self):
        """Test creating mock request with None parameter."""
        parent = Mock()
        parent.item = Mock(name="test_item")

        mock_req = create_mock_request(None, parent)

        # NoneParam should handle dict operations
        assert "key" not in mock_req.param
        assert not mock_req.param
        assert mock_req.param.get("key", "default") == "default"
        assert str(mock_req.param) == "None"

        with pytest.raises(KeyError):
            _ = mock_req.param["key"]

    def test_handle_sync_generator_fixture(self):
        """Test handling a sync generator fixture."""
        teardown_called = False

        def sync_gen_fixture():
            nonlocal teardown_called
            yield "yielded_value"
            teardown_called = True

        finalizers = []
        gen = sync_gen_fixture()

        result = handle_sync_generator_fixture(gen, finalizers)

        assert result == "yielded_value"
        assert len(finalizers) == 1
        assert not teardown_called

        # Execute the finalizer
        finalizers[0]()
        assert teardown_called

    def test_handle_sync_generator_fixture_error_in_teardown(self):
        """Test that errors in sync generator teardown are handled."""

        def sync_gen_fixture():
            yield "value"
            raise ValueError("teardown error")

        finalizers = []
        gen = sync_gen_fixture()

        result = handle_sync_generator_fixture(gen, finalizers)
        assert result == "value"

        # Teardown should not raise but will print error
        import io
        import sys

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output

        try:
            finalizers[0]()  # Should print error but not raise
            output = captured_output.getvalue()
            assert "Error in fixture teardown: teardown error" in output
        finally:
            sys.stdout = old_stdout

    def test_handle_sync_generator_fixture_multiple_yields(self):
        """Test that only first yield is used from sync generator."""

        def multi_yield_fixture():
            yield "first"
            yield "second"  # Should not be reached in normal usage

        finalizers = []
        gen = multi_yield_fixture()

        result = handle_sync_generator_fixture(gen, finalizers)
        assert result == "first"

        # Finalizer should consume the second yield without error
        finalizers[0]()  # Should complete without raising

    def test_create_mock_request_fixture_stack(self):
        """Test that mock request provides _get_fixturestack method."""
        parent = Mock()
        parent.item = Mock()

        mock_req = create_mock_request(None, parent)

        # Should have the method for compatibility
        assert hasattr(mock_req, "_get_fixturestack")
        assert mock_req._get_fixturestack() == []

    @pytest.mark.asyncio
    async def test_parametrized_fixture_with_callspec(self):
        """Test parametrized fixtures with callspec."""
        # Create mock item with callspec
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        # Create a parametrized fixture
        def param_fixture(request):
            return f"value_{request.param}"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = param_fixture
        fixture_def.scope = "function"
        fixture_def.params = ["a", "b", "c"]

        # Set up fixture manager with getfixturedefs
        mock_fm = create_mock_fixture_manager({"param_fixture": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        # Add callspec with params
        mock_item.callspec = MagicMock()
        mock_item.callspec.params = {"param_fixture": "test_param"}

        request = DeferredFixtureRequest(mock_item)

        # Get the parametrized fixture
        value = await request.getfixturevalue("param_fixture")
        assert value == "value_test_param"

    @pytest.mark.asyncio
    async def test_parametrized_fixture_without_callspec(self):
        """Test parametrized fixtures when callspec doesn't have params."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        def param_fixture(request):
            # Should handle None param gracefully
            if hasattr(request, "param") and request.param:
                return f"value_{request.param}"
            return "default_value"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = param_fixture
        fixture_def.scope = "function"
        fixture_def.params = ["a", "b"]

        mock_fm = create_mock_fixture_manager({"param_fixture": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        # Callspec without params attribute
        mock_item.callspec = MagicMock()
        del mock_item.callspec.params

        request = DeferredFixtureRequest(mock_item)

        value = await request.getfixturevalue("param_fixture")
        assert value == "default_value"

    @pytest.mark.asyncio
    async def test_module_scoped_fixture_caching(self):
        """Test that module-scoped fixtures are cached."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        call_count = 0

        def module_fixture():
            nonlocal call_count
            call_count += 1
            return f"module_value_{call_count}"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = module_fixture
        fixture_def.scope = "module"
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"module_fixture": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        request = DeferredFixtureRequest(mock_item)

        # First call
        value1 = await request.getfixturevalue("module_fixture")
        assert value1 == "module_value_1"
        assert call_count == 1

        # Second call should return cached value
        value2 = await request.getfixturevalue("module_fixture")
        assert value2 == "module_value_1"  # Same value
        assert call_count == 1  # Not called again

    @pytest.mark.asyncio
    async def test_fixture_lookup_error(self):
        """Test that FixtureLookupError is raised for missing fixtures."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()
        mock_fm = MagicMock()
        mock_fm.getfixturedefs.return_value = None  # No fixture found
        mock_item.session._fixturemanager = mock_fm

        request = DeferredFixtureRequest(mock_item)

        with pytest.raises(pytest.FixtureLookupError) as exc_info:
            await request.getfixturevalue("nonexistent")

        assert exc_info.value.argname == "nonexistent"

    @pytest.mark.asyncio
    async def test_async_coroutine_fixture(self):
        """Test async coroutine fixtures work correctly."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        async def async_fixture():
            await asyncio.sleep(0.001)
            return "async_value"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = async_fixture
        fixture_def.scope = "function"
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"async_fixture": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        request = DeferredFixtureRequest(mock_item)

        value = await request.getfixturevalue("async_fixture")
        assert value == "async_value"

    @pytest.mark.asyncio
    async def test_fixture_dependencies(self):
        """Test fixtures with dependencies on other fixtures."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        def base_fixture():
            return "base"

        def dependent_fixture(base_fixture):
            return f"dependent_{base_fixture}"

        base_def = MagicMock(spec=FixtureDef)
        base_def.func = base_fixture
        base_def.scope = "function"
        base_def.params = None

        dep_def = MagicMock(spec=FixtureDef)
        dep_def.func = dependent_fixture
        dep_def.scope = "function"
        dep_def.params = None

        mock_fm = create_mock_fixture_manager(
            {
                "base_fixture": [base_def],
                "dependent_fixture": [dep_def],
            }
        )
        mock_item.session._fixturemanager = mock_fm

        request = DeferredFixtureRequest(mock_item)

        value = await request.getfixturevalue("dependent_fixture")
        assert value == "dependent_base"

    @pytest.mark.asyncio
    async def test_teardown_with_mixed_finalizers(self):
        """Test teardown with both sync and async finalizers."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        teardown_order = []

        def sync_gen():
            yield "sync"
            teardown_order.append("sync_teardown")

        async def async_gen():
            yield "async"
            teardown_order.append("async_teardown")

        sync_def = MagicMock(spec=FixtureDef)
        sync_def.func = sync_gen
        sync_def.scope = "function"
        sync_def.params = None

        async_def = MagicMock(spec=FixtureDef)
        async_def.func = async_gen
        async_def.scope = "function"
        async_def.params = None

        mock_fm = create_mock_fixture_manager(
            {
                "sync_fixture": [sync_def],
                "async_fixture": [async_def],
            }
        )
        mock_item.session._fixturemanager = mock_fm

        request = DeferredFixtureRequest(mock_item)

        # Get both fixtures
        sync_val = await request.getfixturevalue("sync_fixture")
        async_val = await request.getfixturevalue("async_fixture")

        assert sync_val == "sync"
        assert async_val == "async"
        assert teardown_order == []

        # Teardown
        await request.teardown()

        # Teardown should happen in reverse order
        assert teardown_order == ["async_teardown", "sync_teardown"]


class TestMockRequest:
    """Test the MockRequest class created by create_mock_request."""

    def test_mock_request_with_dict_param(self):
        """Test MockRequest with dictionary parameter."""
        parent = Mock()
        parent.item = Mock(name="test_item")

        param = {"key": "value", "nested": {"inner": "data"}}
        mock_req = create_mock_request(param, parent)

        # Test dict operations
        assert "key" in mock_req.param
        assert mock_req.param["key"] == "value"
        assert mock_req.param.get("missing", "default") == "default"
        assert mock_req.param["nested"]["inner"] == "data"

    def test_mock_request_none_param_dict_operations(self):
        """Test NoneParam supports all dict-like operations."""
        parent = Mock()
        parent.item = Mock()

        mock_req = create_mock_request(None, parent)
        none_param = mock_req.param

        # Test __contains__
        assert "anything" not in none_param

        # Test get with default
        assert none_param.get("key") is None
        assert none_param.get("key", "default") == "default"

        # Test __getitem__ raises KeyError
        with pytest.raises(KeyError, match="'key' not found in None param"):
            _ = none_param["key"]

        # Test string representations
        assert str(none_param) == "None"
        assert repr(none_param) == "None"

        # Test boolean evaluation
        assert not none_param
        if none_param:
            pytest.fail("NoneParam should be falsy")

    @pytest.mark.asyncio
    async def test_mock_request_getfixturevalue_delegation(self):
        """Test that MockRequest delegates getfixturevalue correctly."""
        parent = Mock()
        parent.item = Mock()

        # Make parent's getfixturevalue async
        async def async_getfixturevalue(name):
            return f"fixture_{name}"

        parent.getfixturevalue = async_getfixturevalue

        mock_req = create_mock_request("param_value", parent)

        # Test delegation
        value = await mock_req.getfixturevalue("test_fixture")
        assert value == "fixture_test_fixture"

    def test_mock_request_fixturestack(self):
        """Test MockRequest provides _get_fixturestack for compatibility."""
        parent = Mock()
        parent.item = Mock()

        mock_req = create_mock_request(None, parent)

        stack = mock_req._get_fixturestack()
        assert isinstance(stack, list)
        assert len(stack) == 0


class TestResolveFixtureDependencies:
    """Test the resolve_fixture_dependencies function."""

    @pytest.mark.asyncio
    async def test_resolve_with_no_code_attribute(self):
        """Test resolving dependencies for objects without __code__."""
        # Built-in functions don't have __code__
        import math

        func = math.sqrt  # Built-in function

        parent = Mock()
        kwargs = await resolve_fixture_dependencies(func, None, parent)

        assert kwargs == {}

    @pytest.mark.asyncio
    async def test_resolve_skips_self_parameter(self):
        """Test that 'self' parameter is skipped."""

        class MyClass:
            def method(self, fixture_a, fixture_b):
                pass

        obj = MyClass()
        parent = Mock()

        async def mock_getfixturevalue(name):
            return f"value_{name}"

        parent.getfixturevalue = mock_getfixturevalue

        kwargs = await resolve_fixture_dependencies(obj.method, None, parent)

        assert "self" not in kwargs
        assert kwargs["fixture_a"] == "value_fixture_a"
        assert kwargs["fixture_b"] == "value_fixture_b"


class TestHelperFunctions:
    """Test the helper functions."""

    @pytest.mark.asyncio
    async def test_handle_async_generator_with_stopasynciteration(self):
        """Test async generator that ends normally with StopAsyncIteration."""

        async def async_gen():
            yield "value"
            # Generator ends normally - no more yields

        finalizers = []
        gen = async_gen()

        value = await handle_async_generator_fixture(gen, finalizers)
        assert value == "value"
        assert len(finalizers) == 1

        # Finalizer should handle StopAsyncIteration gracefully
        await finalizers[0]()  # Should not raise

    @pytest.mark.asyncio
    async def test_handle_async_generator_with_error(self):
        """Test async generator with error in teardown."""
        error_raised = False

        async def async_gen_with_error():
            nonlocal error_raised
            yield "value"
            error_raised = True
            raise RuntimeError("Teardown failed")

        finalizers = []
        gen = async_gen_with_error()

        value = await handle_async_generator_fixture(gen, finalizers)
        assert value == "value"
        assert not error_raised

        # Capture print output
        import io
        import sys

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            await finalizers[0]()
            output = captured.getvalue()
            assert "Error in async fixture teardown: Teardown failed" in output
        finally:
            sys.stdout = old_stdout

        assert error_raised

    def test_handle_sync_generator_with_stopiteration(self):
        """Test sync generator that ends normally."""

        def sync_gen():
            yield "value"
            # Generator ends normally

        finalizers = []
        gen = sync_gen()

        value = handle_sync_generator_fixture(gen, finalizers)
        assert value == "value"
        assert len(finalizers) == 1

        # Finalizer should handle StopIteration gracefully
        finalizers[0]()  # Should not raise


class TestFixtureManager:
    """Test the FixtureManager class."""

    @pytest.mark.asyncio
    async def test_create_fixtures_with_wrapped_function(self):
        """Test creating fixtures for a wrapped function."""

        # Create wrapped function
        def original(col1, col2, fixture1):
            pass

        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        wrapper.__wrapped__ = original
        wrapper._column_names = ["col1", "col2"]

        # Mock item
        mock_item = MagicMock()
        mock_item.function = wrapper
        mock_item.session = MagicMock()

        # Setup fixture
        def fixture1_func():
            return "fixture1_value"

        fixture1_def = MagicMock(spec=FixtureDef)
        fixture1_def.func = fixture1_func
        fixture1_def.scope = "function"
        fixture1_def.params = None

        mock_fm = create_mock_fixture_manager({"fixture1": [fixture1_def]})
        mock_item.session._fixturemanager = mock_fm

        # Create fixtures
        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Should only have fixture1, not the column names
        assert "fixture1" in fixtures
        assert fixtures["fixture1"] == "fixture1_value"
        assert "col1" not in fixtures
        assert "col2" not in fixtures

    @pytest.mark.asyncio
    async def test_create_fixtures_with_no_column_names(self):
        """Test creating fixtures when function has no _column_names."""

        def eval_func(fixture1, fixture2):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func  # No _column_names attribute
        mock_item.session = MagicMock()

        # Setup fixtures
        def fixture1_func():
            return "value1"

        def fixture2_func():
            return "value2"

        fixture1_def = MagicMock(spec=FixtureDef)
        fixture1_def.func = fixture1_func
        fixture1_def.scope = "function"
        fixture1_def.params = None

        fixture2_def = MagicMock(spec=FixtureDef)
        fixture2_def.func = fixture2_func
        fixture2_def.scope = "function"
        fixture2_def.params = None

        mock_fm = create_mock_fixture_manager(
            {
                "fixture1": [fixture1_def],
                "fixture2": [fixture2_def],
            }
        )
        mock_item.session._fixturemanager = mock_fm

        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Should create all parameters as fixtures
        assert fixtures["fixture1"] == "value1"
        assert fixtures["fixture2"] == "value2"

    @pytest.mark.asyncio
    async def test_create_fixtures_with_fixture_lookup_error(self):
        """Test that fixture lookup errors are handled gracefully."""

        def eval_func(existing_fixture, missing_fixture):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # Only setup one fixture
        def existing_func():
            return "exists"

        existing_def = MagicMock(spec=FixtureDef)
        existing_def.func = existing_func
        existing_def.scope = "function"
        existing_def.params = None

        mock_fm = create_mock_fixture_manager({"existing_fixture": [existing_def]})
        mock_item.session._fixturemanager = mock_fm

        # Capture print output
        import io
        import sys

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            fixtures, request = await FixtureManager.create_fixtures(mock_item)

            # Should have the existing fixture but not the missing one
            assert "existing_fixture" in fixtures
            assert "missing_fixture" not in fixtures

            # Check if error was printed (it might be caught silently)
            _ = captured.getvalue()
            # FixtureLookupError is caught silently, no print expected
        finally:
            sys.stdout = old_stdout

    @pytest.mark.asyncio
    async def test_create_fixtures_with_general_exception(self):
        """Test that general exceptions during fixture creation are handled."""

        def eval_func(broken_fixture):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # Create a fixture that raises an exception
        def broken_func():
            raise RuntimeError("Fixture creation failed")

        broken_def = MagicMock(spec=FixtureDef)
        broken_def.func = broken_func
        broken_def.scope = "function"
        broken_def.params = None

        mock_fm = create_mock_fixture_manager({"broken_fixture": [broken_def]})
        mock_item.session._fixturemanager = mock_fm

        # Capture print output
        import io
        import sys

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            fixtures, request = await FixtureManager.create_fixtures(mock_item)

            # Should not have the broken fixture
            assert "broken_fixture" not in fixtures

            # Should have printed an error message
            output = captured.getvalue()
            assert "Failed to create fixture broken_fixture" in output
            assert "Fixture creation failed" in output
        finally:
            sys.stdout = old_stdout

    @pytest.mark.asyncio
    async def test_teardown_fixtures(self):
        """Test the teardown_fixtures static method."""
        mock_request = MagicMock()

        # Make teardown async
        async def async_teardown():
            mock_request.teardown_called = True

        mock_request.teardown = async_teardown

        await FixtureManager.teardown_fixtures(mock_request)

        assert mock_request.teardown_called is True

    @pytest.mark.asyncio
    async def test_teardown_with_sync_finalizer_exception(self):
        """Test teardown with synchronous finalizer that raises exception."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()
        mock_item.session._fixturemanager = MagicMock()
        mock_item.session._fixturemanager._arg2fixturedefs = {}

        request = DeferredFixtureRequest(mock_item)

        # Manually add a finalizer that raises an exception
        def failing_finalizer():
            raise RuntimeError("Finalizer failed")

        request._finalizers.append(failing_finalizer)

        # Capture print output
        import io
        import sys

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            await request.teardown()
            output = captured.getvalue()
            assert "Error in finalizer: Finalizer failed" in output
        finally:
            sys.stdout = old_stdout

    @pytest.mark.asyncio
    async def test_cached_function_scoped_fixture(self):
        """Test that function-scoped fixtures are not cached."""
        mock_item = MagicMock()
        mock_item.session = MagicMock()

        call_count = 0

        def function_scoped():
            nonlocal call_count
            call_count += 1
            return f"value_{call_count}"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = function_scoped
        fixture_def.scope = "function"  # Function scope
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"func_fixture": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        request = DeferredFixtureRequest(mock_item)

        # First call
        value1 = await request.getfixturevalue("func_fixture")
        assert value1 == "value_1"
        assert call_count == 1

        # Manually add to cache (simulating caching)
        request._fixture_values["func_fixture"] = value1

        # Second call - should NOT use cache for function-scoped
        value2 = await request.getfixturevalue("func_fixture")
        assert value2 == "value_2"  # New value, not cached
        assert call_count == 2  # Called again


class TestDirectParametrization:
    """Test handling of direct parametrization in FixtureManager."""

    @pytest.mark.asyncio
    async def test_create_fixtures_with_direct_param(self):
        """Test that direct parametrization values are included in fixtures."""

        def eval_func(dataset_col, fixture_param, direct_param):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # Add callspec with direct parameter
        mock_item.callspec = MagicMock()
        mock_item.callspec.params = {"direct_param": "direct_value"}

        # Set up fixture for fixture_param only
        def fixture_func():
            return "fixture_value"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = fixture_func
        fixture_def.scope = "function"
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"fixture_param": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        # Mark dataset_col as a column name
        eval_func._column_names = ["dataset_col"]

        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Should have both fixture and direct param, but not dataset column
        assert "fixture_param" in fixtures
        assert fixtures["fixture_param"] == "fixture_value"
        assert "direct_param" in fixtures
        assert fixtures["direct_param"] == "direct_value"
        assert "dataset_col" not in fixtures

    @pytest.mark.asyncio
    async def test_create_fixtures_with_multiple_direct_params(self):
        """Test multiple direct parametrization values."""

        def eval_func(col1, col2, fixture1, direct1, direct2):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # Add callspec with multiple direct parameters
        mock_item.callspec = MagicMock()
        mock_item.callspec.params = {
            "direct1": "value1",
            "direct2": 42,
            "fixture1": "ignored",  # This will be handled as indirect
        }

        # Set up fixture
        def fixture1_func():
            return "fixture1_value"

        fixture1_def = MagicMock(spec=FixtureDef)
        fixture1_def.func = fixture1_func
        fixture1_def.scope = "function"
        fixture1_def.params = None

        mock_fm = create_mock_fixture_manager({"fixture1": [fixture1_def]})
        mock_item.session._fixturemanager = mock_fm

        # Mark columns
        eval_func._column_names = ["col1", "col2"]

        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Check all expected values
        assert fixtures["fixture1"] == "fixture1_value"  # From fixture
        assert fixtures["direct1"] == "value1"  # Direct param
        assert fixtures["direct2"] == 42  # Direct param
        assert "col1" not in fixtures  # Dataset column
        assert "col2" not in fixtures  # Dataset column

    @pytest.mark.asyncio
    async def test_indirect_param_takes_precedence(self):
        """Test that indirect parametrization (fixtures) takes precedence."""

        def eval_func(param_name):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # Add to callspec (would be direct if no fixture exists)
        mock_item.callspec = MagicMock()
        mock_item.callspec.params = {"param_name": "indirect_value"}

        # But also create a fixture for it (making it indirect)
        def param_fixture(request):
            return f"fixture_got_{request.param}"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = param_fixture
        fixture_def.scope = "function"
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"param_name": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        # Create mock request for the fixture
        mock_request = create_mock_request(
            "indirect_value", DeferredFixtureRequest(mock_item)
        )
        fixture_def.func = lambda: param_fixture(mock_request)

        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Should use fixture value (indirect), not direct value
        assert fixtures["param_name"] == "fixture_got_indirect_value"

    @pytest.mark.asyncio
    async def test_create_fixtures_no_callspec(self):
        """Test that missing callspec doesn't cause errors."""

        def eval_func(fixture_param):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # No callspec attribute
        del mock_item.callspec

        # Set up fixture
        def fixture_func():
            return "fixture_value"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = fixture_func
        fixture_def.scope = "function"
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"fixture_param": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Should still get fixture value
        assert fixtures["fixture_param"] == "fixture_value"

    @pytest.mark.asyncio
    async def test_mixed_direct_and_indirect_params(self):
        """Test evaluation with both direct and indirect parametrization."""

        def eval_func(data_col, direct_param, indirect_fixture):
            pass

        mock_item = MagicMock()
        mock_item.function = eval_func
        mock_item.session = MagicMock()

        # Callspec with both types
        mock_item.callspec = MagicMock()
        mock_item.callspec.params = {
            "direct_param": "direct_val",
            "indirect_fixture": "param_for_fixture",
        }

        # Set up indirect fixture
        def indirect_func(request):
            return f"processed_{request.param}"

        fixture_def = MagicMock(spec=FixtureDef)
        fixture_def.func = indirect_func
        fixture_def.scope = "function"
        fixture_def.params = None

        mock_fm = create_mock_fixture_manager({"indirect_fixture": [fixture_def]})
        mock_item.session._fixturemanager = mock_fm

        # Create mock request for the fixture
        mock_request = create_mock_request(
            "param_for_fixture", DeferredFixtureRequest(mock_item)
        )
        fixture_def.func = lambda: indirect_func(mock_request)

        # Mark data column
        eval_func._column_names = ["data_col"]

        fixtures, request = await FixtureManager.create_fixtures(mock_item)

        # Check results
        assert "direct_param" in fixtures
        assert fixtures["direct_param"] == "direct_val"
        assert "indirect_fixture" in fixtures
        assert fixtures["indirect_fixture"] == "processed_param_for_fixture"
        assert "data_col" not in fixtures
