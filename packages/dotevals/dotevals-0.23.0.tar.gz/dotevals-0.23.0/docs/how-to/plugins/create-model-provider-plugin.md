# How to Create a Model Provider Plugin

This guide walks you through creating a custom model provider plugin for dotevals, from implementation to distribution.

## Overview

Model provider plugins allow you to:

- Manage model clients and connections independently of execution environments
- Share reusable model providers with the community
- Integrate custom model services with dotevals's evaluation framework
- Handle resource lifecycle (setup, sharing, cleanup) efficiently

## Step 1: Set Up Your Project

Create a new directory for your model provider plugin:

```bash
mkdir my-model-provider
cd my-model-provider
```

Set up the project structure:

```
my-model-provider/
├── pyproject.toml
├── README.md
├── src/
│   └── my_model_provider/
│       ├── __init__.py
│       ├── provider.py
│       └── conftest.py
└── tests/
    └── test_provider.py
```

## Step 2: Create the Provider Class

In `src/my_model_provider/provider.py`:

```python
from dotevals.providers import ModelProvider, ModelHandle
from typing import Dict, Any


class MyModelProvider(ModelProvider):
    """A custom model provider for managing model resources."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the provider.

        Args:
            config: Provider-specific configuration
        """
        # Your initialization logic here
        pass

    async def setup(self, resource_spec: str, **kwargs) -> ModelHandle:
        """Setup a model resource and return a handle.

        Args:
            resource_spec: Model identifier or specification
            **kwargs: Additional setup parameters

        Returns:
            ModelHandle with model client and teardown method
        """
        # Your setup logic here
        # Must return ModelHandle(resource_id, model, manager)
        pass

    async def teardown(self, resource_id: str) -> None:
        """Tear down a specific resource.

        Args:
            resource_id: The resource to clean up
        """
        # Your cleanup logic here
        pass
```

!!! info "ModelHandle Pattern"
    All model providers must return a `ModelHandle` from `setup()`. This provides a consistent interface for resource management across all providers.

## Step 3: Create Pytest Fixtures

In `src/my_model_provider/conftest.py`:

```python
import pytest
import asyncio


@pytest.fixture(scope="session")
def my_model_provider():
    """Session-scoped model provider."""
    from .provider import MyModelProvider

    provider = MyModelProvider()

    # Ensure cleanup at session end
    def cleanup():
        # Your session cleanup logic
        pass

    yield provider
    cleanup()


@pytest.fixture
async def my_model_client(request, my_model_provider):
    """Standard model provider fixture pattern."""
    handle = await my_model_provider.setup(request.param)
    yield handle.model
    await handle.teardown()
```

## Step 4: Configure Package Entry Points

Create `pyproject.toml` with the following section to register your provider:

```toml
# Register your model provider as an entry point
[project.entry-points."dotevals.model_providers"]
my_model = "my_model_provider.conftest:my_model_provider"

# Register pytest plugin
[project.entry-points.pytest11]
my_model_provider = "my_model_provider.conftest"
```

!!! tip "Complete pyproject.toml"
    You'll also need standard Python package metadata (name, version, dependencies, etc.). See the [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for a complete example.

## Step 5: Add Tests

Create tests in `tests/test_provider.py` to verify your provider works correctly:

- Test provider initialization with valid configuration
- Test resource setup and teardown lifecycle
- Test error handling for invalid resource specifications
- Test concurrent access and resource sharing

## Step 6: Add Documentation

Create a comprehensive `README.md` with usage examples and configuration options.

## Step 7: Test Locally

Before publishing, test your provider locally:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Test integration with dotevals
python -c "from dotevals.providers import list_available; print(list_available())"
```

## Step 8: Publish to PyPI

Once your provider is published, users can install and use it:

```bash
pip install my-model-provider
```

## Usage

Once users install your model provider plugin from PyPI, they can use the fixtures you provided without any additional configuration. The provider is automatically discovered and available:

```python
import pytest
from dotevals import foreach
from dotevals.evaluators import exact_match

@pytest.mark.parametrize("my_model_client", ["model-v1", "model-v2"], indirect=True)
@foreach("prompt,expected", test_data)
def eval_with_my_provider(prompt, expected, my_model_client):
    response = my_model_client.generate(prompt)
    return exact_match(response, expected)
```

The `my_model_client` fixture is the one you defined in Step 3 of your plugin. Users can parametrize it to test different model configurations.

## Troubleshooting

### Provider Not Found

If your provider doesn't appear in `list_available()`:

1. Check the entry point name matches exactly
2. Ensure the package is installed (`pip list | grep my-model`)
3. Verify the module path in entry points is correct

### Resource Setup Failures

If resources fail to setup:

1. Check that all dependencies are available
2. Verify configuration parameters are correct
3. Test resource creation directly outside of dotevals

## See Also

- [Model Provider Pattern](../model-provider-pattern.md) - Detailed pattern explanation
- [Plugin Architecture](../../explanation/plugin-architecture.md) - Plugin system overview
- [Tutorial 2: Using Real Models](../../tutorials/02-using-real-models.md) - Examples using providers
