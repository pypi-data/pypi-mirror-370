"""Fixture lifecycle management for deferred evaluation execution.

Normally, pytest fixtures are created and torn down during the collection phase,
but dotevals evaluations are executed later during session finalization. This
module provides infrastructure to create fixtures on-demand during evaluation
execution while maintaining proper lifecycle management.

The key components are:
- DeferredFixtureRequest: Provides fixture values on-demand with proper teardown
- FixtureManager: Coordinates fixture creation and teardown for evaluations
"""

import asyncio
import inspect
from collections.abc import Callable
from typing import Any, TypeAlias

import pytest
from _pytest.fixtures import FixtureDef

# Type aliases for fixture-related types
FixtureValue: TypeAlias = Any
FixtureDict: TypeAlias = dict[str, FixtureValue]
Finalizer: TypeAlias = Callable[[], None]
AsyncFinalizer: TypeAlias = Callable[[], Any]  # Returns Awaitable


# Helper functions for fixture execution
def create_mock_request(
    param_value: FixtureValue, parent_request: "DeferredFixtureRequest"
) -> Any:
    """Create a mock request object for fixtures that expect 'request' parameter.

    Args:
        param_value: The parameter value for parametrized fixtures
        parent_request: The parent DeferredFixtureRequest

    Returns:
        A mock request object with the necessary attributes and methods
    """

    class MockRequest:
        def __init__(self, param_value, parent_request):
            self._param = param_value
            self.node = parent_request.item
            self.item = parent_request.item
            self._parent = parent_request

        @property
        def param(self):
            """Property to handle None param values gracefully."""
            if self._param is None:
                # Return a mock object that handles 'in' checks and dict operations
                class NoneParam:
                    def __contains__(self, item):
                        return False

                    def __str__(self):
                        return "None"

                    def __repr__(self):
                        return "None"

                    def __bool__(self):
                        return False

                    def get(self, key, default=None):
                        """Support dict-like get operations."""
                        return default

                    def __getitem__(self, key):
                        """Support dict-like indexing."""
                        raise KeyError(f"'{key}' not found in None param")

                return NoneParam()
            return self._param

        async def getfixturevalue(self, name):
            # Delegate to the parent DeferredFixtureRequest
            return await self._parent.getfixturevalue(name)

        # Add _get_fixturestack for compatibility
        def _get_fixturestack(self):
            return []

    return MockRequest(param_value, parent_request)


async def resolve_fixture_dependencies(
    func: Callable, param: Any, parent_request: "DeferredFixtureRequest"
) -> FixtureDict:
    """Resolve all dependencies for a fixture function.

    Args:
        func: The fixture function
        param: Optional parameter value for parametrized fixtures
        parent_request: The DeferredFixtureRequest to use for resolving dependencies

    Returns:
        Dictionary of resolved dependencies to pass as kwargs
    """
    kwargs = {}
    if hasattr(func, "__code__"):
        argnames = func.__code__.co_varnames[: func.__code__.co_argcount]
        for dep_name in argnames:
            if dep_name == "request":
                kwargs["request"] = create_mock_request(param, parent_request)
            elif dep_name != "self":
                kwargs[dep_name] = await parent_request.getfixturevalue(dep_name)
    return kwargs


def handle_sync_generator_fixture(
    result: Any, finalizers: list[Finalizer]
) -> FixtureValue:
    """Handle a synchronous generator fixture (yield fixture).

    Args:
        result: The generator from the fixture function
        finalizers: List to append the teardown finalizer to

    Returns:
        The yielded value from the fixture
    """
    value = next(result)

    # Register finalizer
    def finalizer():
        try:
            next(result)
        except StopIteration:
            pass
        except Exception as e:
            print(f"Error in fixture teardown: {e}")

    finalizers.append(finalizer)
    return value


async def handle_async_generator_fixture(
    result: Any, finalizers: list[AsyncFinalizer]
) -> FixtureValue:
    """Handle an asynchronous generator fixture (async yield fixture).

    Args:
        result: The async generator from the fixture function
        finalizers: List to append the teardown finalizer to

    Returns:
        The yielded value from the fixture
    """
    value = await result.__anext__()

    # Register async finalizer
    async def async_finalizer():
        try:
            await result.__anext__()
        except StopAsyncIteration:
            pass
        except Exception as e:
            print(f"Error in async fixture teardown: {e}")

    finalizers.append(async_finalizer)
    return value


class DeferredFixtureRequest:
    """A wrapper that provides fixture values on-demand during evaluation execution.

    This class recreates pytest's fixture resolution logic for deferred execution.
    It handles fixture creation, caching based on scope, dependency injection,
    and proper teardown through finalizers.

    Key features:
    - Respects fixture scoping (function, module, session)
    - Handles fixture dependencies automatically
    - Supports parametrized fixtures
    - Manages cleanup through finalizers

    Attributes:
        item: The pytest Item being evaluated
        _fixture_defs: Map of fixture name to FixtureDef from pytest
        _fixture_values: Cache for non-function scoped fixture values
        _finalizers: Stack of cleanup functions to run on teardown
    """

    def __init__(self, item: pytest.Item):
        self.item = item
        self._fixture_values: dict[str, Any] = {}
        self._finalizers: list = []

        # Store fixture manager for on-demand resolution
        if hasattr(item, "session") and hasattr(item.session, "_fixturemanager"):
            self._fixture_manager = item.session._fixturemanager
        else:
            self._fixture_manager = None

    def _get_fixturestack(self):
        """Return the fixture stack for compatibility with pytest.FixtureLookupError."""
        return []

    async def getfixturevalue(self, argname: str) -> Any:
        """Get or create a fixture value.

        This method implements the core fixture resolution logic. It:
        1. Checks if the fixture is already cached (for non-function scoped)
        2. Creates the fixture if needed, handling dependencies
        3. Caches the result based on scope
        4. Registers any teardown logic

        Args:
            argname: Name of the fixture to retrieve

        Returns:
            The fixture value

        Raises:
            pytest.FixtureLookupError: If the fixture is not found
        """
        # Don't cache function-scoped fixtures - create fresh for each evaluation
        # Check cache for non-function scoped fixtures
        if argname in self._fixture_values:
            # Need to get fixture def to check scope
            if self._fixture_manager:
                defs = self._fixture_manager.getfixturedefs(argname, self.item)
                if defs and defs[-1].scope != "function":
                    return self._fixture_values[argname]

        # Get fixture definition using pytest's proper resolution
        if not self._fixture_manager:
            raise pytest.FixtureLookupError(argname, self)

        defs = self._fixture_manager.getfixturedefs(argname, self.item)
        if not defs:
            raise pytest.FixtureLookupError(argname, self)

        # Use the most specific fixture definition (last in the list)
        fixture_def = defs[-1]

        # Create the fixture value
        # Check if there's a parameter for this fixture in the callspec (indirect parametrization)
        callspec = getattr(self.item, "callspec", None)
        param = None
        if callspec and hasattr(callspec, "params") and argname in callspec.params:
            param = callspec.params.get(argname)

        if param is not None or (hasattr(fixture_def, "params") and fixture_def.params):
            # Either we have a param from indirect parametrization or the fixture has its own params
            fixture_value = await self._execute_fixture_def(fixture_def, param)
        else:
            fixture_value = await self._execute_fixture_def(fixture_def)

        # Only cache non-function scoped fixtures
        if fixture_def.scope != "function":
            self._fixture_values[argname] = fixture_value

        return fixture_value

    async def _execute_fixture_def(self, fixture_def: FixtureDef, param=None) -> Any:
        """Execute a fixture definition and handle its lifecycle.

        This method coordinates the fixture execution process by:
        1. Resolving fixture dependencies
        2. Executing the fixture function
        3. Handling different fixture types (sync, async, generators)
        4. Registering teardown finalizers

        Args:
            fixture_def: The pytest FixtureDef to execute
            param: Optional parameter value for parametrized fixtures

        Returns:
            The fixture value (or yielded value for generator fixtures)
        """
        # Resolve dependencies
        kwargs = await resolve_fixture_dependencies(fixture_def.func, param, self)

        # Execute the fixture function
        result = fixture_def.func(**kwargs)

        # Check for generators first (they can also be detected as coroutines)
        if hasattr(result, "__anext__"):
            return await handle_async_generator_fixture(result, self._finalizers)
        elif hasattr(result, "__next__"):
            return handle_sync_generator_fixture(result, self._finalizers)
        elif asyncio.iscoroutine(result):
            return await result
        else:
            return result

    async def teardown(self):
        """Execute all registered finalizers in reverse order.

        This ensures proper cleanup of resources created during fixture setup.
        Finalizers are run in LIFO order to respect dependency relationships.
        Errors during teardown are logged but don't stop other finalizers.
        """
        for finalizer in reversed(self._finalizers):
            try:
                if asyncio.iscoroutinefunction(finalizer):
                    await finalizer()
                else:
                    finalizer()
            except Exception as e:
                print(f"Error in finalizer: {e}")
        self._finalizers.clear()
        self._fixture_values.clear()


class FixtureManager:
    """Manages fixture lifecycle for deferred evaluation execution.

    This class provides static methods to coordinate fixture creation and
    teardown for dotevals evaluations. It bridges the gap between pytest's
    fixture system and dotevals's deferred execution model.
    """

    @staticmethod
    async def create_fixtures(
        item: pytest.Item,
    ) -> tuple[FixtureDict, DeferredFixtureRequest]:
        """Create fixtures for an evaluation item.

        This method:
        1. Analyzes the evaluation function to determine required fixtures
        2. Excludes dataset columns from fixture resolution
        3. Creates all required fixtures using DeferredFixtureRequest
        4. Returns both the fixture values and the request for teardown

        The key insight is separating dataset parameters (handled by @foreach)
        from fixture parameters (handled by pytest).

        Args:
            item: The pytest Item containing the evaluation function

        Returns:
            Tuple of (fixture_values dict, DeferredFixtureRequest for teardown)
        """
        eval_fn = item.function
        original_func = getattr(eval_fn, "__wrapped__", eval_fn)

        # Get expected parameters
        sig = inspect.signature(original_func)
        expected_params = set(sig.parameters.keys())

        # Get dataset columns to exclude
        column_names = getattr(eval_fn, "_column_names", [])
        columns = set(column_names)
        expected_fixture_params = expected_params - columns

        # Create deferred request
        request = DeferredFixtureRequest(item)

        # Create fixtures and handle direct parametrizations
        fixture_values = {}

        # Check for direct parametrizations first
        callspec = getattr(item, "callspec", None)
        if callspec and hasattr(callspec, "params"):
            for param_name in expected_fixture_params:
                if param_name in callspec.params:
                    # Check if this is a direct parametrization (not indirect)
                    # Try to get it as a fixture first
                    try:
                        value = await request.getfixturevalue(param_name)
                        fixture_values[param_name] = value
                    except pytest.FixtureLookupError:
                        # Not a fixture, so it's a direct parametrization
                        fixture_values[param_name] = callspec.params[param_name]

        # Now handle remaining fixtures that aren't parametrizations
        for fixture_name in expected_fixture_params:
            if fixture_name not in fixture_values:
                try:
                    value = await request.getfixturevalue(fixture_name)
                    fixture_values[fixture_name] = value
                except pytest.FixtureLookupError:
                    # Fixture not found - might be optional or provided by a plugin
                    pass
                except Exception as e:
                    # Log all fixture creation errors for debugging
                    print(f"Failed to create fixture {fixture_name}: {e}")

        return fixture_values, request

    @staticmethod
    async def teardown_fixtures(request: DeferredFixtureRequest) -> None:
        """Tear down fixtures after evaluation completes.

        This ensures all fixture finalizers are run, releasing resources
        like file handles, network connections, or model servers.

        Args:
            request: The DeferredFixtureRequest that created the fixtures
        """
        await request.teardown()
