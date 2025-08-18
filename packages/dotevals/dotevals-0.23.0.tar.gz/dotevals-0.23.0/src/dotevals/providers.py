"""Model providers for dotevals - manage model clients, connections, etc.

Model providers are distributed as pytest fixtures and discovered via entry points.
They handle resource lifecycle (creation, caching, teardown) independently of
execution environment (runners).
"""

import importlib.metadata
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class ModelHandle:
    """Handle to a model with its client and lifecycle methods.

    All model providers MUST return this from their setup() method.
    """

    resource_id: str
    model: Any
    manager: "ModelProvider"
    _active: bool = True

    async def teardown(self) -> None:
        """Tear down this specific model resource."""
        if self._active:
            await self.manager.teardown(self.resource_id)
            self._active = False

    @property
    def is_active(self) -> bool:
        """Check if the model resource is still active."""
        return self._active


class ModelProvider(ABC):
    """Base class for all model providers.

    All model providers MUST inherit from this class and implement
    the required methods.

    The standard pattern is:
        ```python
        handle = await provider.setup(model_spec)
        # use handle.model
        await handle.teardown()
        ```
    """

    @abstractmethod
    async def setup(self, resource_spec: str, **config: Any) -> ModelHandle:
        """Set up a model and return a handle.

        Args:
            resource_spec: Specification for the model (e.g., model name)
            **config: Additional configuration parameters

        Returns:
            ModelHandle containing the model client and teardown method

        Example:
            handle = await manager.setup("gpt-4", temperature=0.7)
            response = await handle.model.generate("Hello")
            await handle.teardown()
        """
        pass

    @abstractmethod
    async def teardown(self, resource_id: str) -> None:
        """Tear down a specific resource.

        Args:
            resource_id: The ID of the resource to tear down

        Note:
            This is typically called by the ModelHandle.teardown() method.
        """
        pass


def discover_model_providers() -> dict[str, str]:
    """Discover all installed model provider plugins.

    Model providers are registered via entry points in the "dotevals.model_providers"
    group. Each entry point should map to a fixture name, the individual provider
    fixture defined in the plugin.

    Returns:
        Dictionary mapping provider name to fixture name

    Example:
        In pyproject.toml:
        ```toml
        [project.entry-points."dotevals.model_providers"]
        vllm = "doteval_vllm:vllm_provider"
        ```
    """
    providers = {}

    try:
        # Try the new API first (Python 3.10+)
        entry_points = importlib.metadata.entry_points(group="dotevals.model_providers")
    except TypeError:
        # Fall back to older API
        all_entry_points = importlib.metadata.entry_points()
        if isinstance(all_entry_points, dict):
            # Old API returns dict mapping group names to lists of entry points
            entry_points = all_entry_points.get("dotevals.model_providers", [])  # type: ignore[arg-type]
        else:
            entry_points = []

    for entry_point in entry_points:
        try:
            # The value should be a fixture name
            fixture_name = entry_point.value.split(":")[-1]
            providers[entry_point.name] = fixture_name
        except Exception as e:
            warnings.warn(f"Failed to process model provider {entry_point.name}: {e}")

    return providers


@pytest.fixture(scope="session")
def model_providers(request: pytest.FixtureRequest) -> dict[str, Any]:
    """Auto-discover and provide access to all model providers.

    This fixture discovers all installed model provider plugins and
    provides access to them via a dictionary.

    Returns:
        Dictionary mapping provider name to provider instance

    Example:
        ```python
        def test_with_providers(model_providers):
            vllm_provider = model_providers["vllm"]
            handle = vllm_provider.setup("llama-7b")
            yield handle.model()
            handle.teardown()
        ```
    """
    discovered = discover_model_providers()
    providers = {}

    for name, fixture_name in discovered.items():
        try:
            # Get the fixture value
            if hasattr(request, "getfixturevalue"):
                provider = request.getfixturevalue(fixture_name)
                providers[name] = provider
        except Exception as e:
            warnings.warn(f"Failed to load model provider {name}: {e}")

    return providers
