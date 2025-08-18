# The Model Provider Pattern

This document describes the enforced pattern for model providers in dotevals plugins. All model providers must follow this pattern by inheriting from the `ModelProvider` base class.

## The Pattern

```python
@pytest.fixture
async def client(request, model_providers):
    """Standard model provider fixture pattern."""
    handle = await model_providers.setup(request.param)
    yield handle.client
    await handle.teardown()
```

This pattern provides:
- **Explicit lifecycle** - You see exactly when resources are created/destroyed
- **Clean API** - Just `setup()`, use client, `teardown()`
- **Flexibility** - Works for any resource type
- **Proper cleanup** - Guaranteed teardown even on failure

## Core Components

### 1. Resource Handle

```python
@dataclass
class ResourceHandle:
    """Handle to a resource."""
    resource_id: str
    client: Any
    manager: 'ModelProvider'

    async def teardown(self):
        """Tear down this specific resource."""
        await self.manager.teardown(self.resource_id)
```

### 2. Model Provider

```python
class ModelProvider:
    """Manages model resource lifecycle."""

    async def setup(self, resource_spec: str, **config) -> ResourceHandle:
        """Setup a resource and return a handle."""
        # Create resource
        client = await self._create_resource(resource_spec, **config)

        # Return handle
        return ResourceHandle(
            resource_id=resource_spec,
            client=client,
            manager=self
        )

    async def teardown(self, resource_id: str):
        """Tear down a specific resource."""
        # Cleanup logic
```

### 3. Fixture Pattern

```python
# Session-scoped provider
@pytest.fixture(scope="session")
def model_providers(request):
    """Model provider instance."""
    provider = ModelProvider()
    request.addfinalizer(lambda: asyncio.run(provider.teardown_all()))
    return provider

# Function-scoped client
@pytest.fixture
async def client(request, model_providers):
    """Setup resource and yield client."""
    handle = await model_providers.setup(request.param)
    yield handle.client
    await handle.teardown()
```

## Usage Examples

### Basic Usage

```python
@pytest.mark.parametrize("client", ["model-a", "model-b"], indirect=True)
@foreach("input", dataset)
async def eval_models(input, client):
    """Client is automatically managed."""
    response = await client.generate(input)
    return Result(response)
```

### Manual Control

```python
@foreach("model", ["model-a", "model-b"])
async def eval_with_control(model, model_providers):
    """Explicit lifecycle control."""
    handle = await model_providers.setup(model)
    try:
        response = await handle.client.generate("test")
        return Result(response)
    finally:
        await handle.teardown()
```

### Lazy Pattern (Optional)

```python
@pytest.fixture
async def lazy_client(request, model_providers):
    """Lazy setup - only creates resource if used."""
    lazy_handle = model_providers.request(request.param)
    yield lazy_handle
    await lazy_handle.teardown()  # Only tears down if set up
```

## Why This Pattern?

1. **Consistency** - All model providers follow the same pattern
2. **Explicit** - No hidden magic, clear lifecycle
3. **Composable** - Easy to build higher-level abstractions
4. **Testable** - Easy to mock and test
5. **Pythonic** - Follows Python's context manager patterns

## Implementation Checklist

When implementing a model provider:

- [ ] Create a `ResourceHandle` class with `client` and `teardown()`
- [ ] Implement `setup()` method returning a handle
- [ ] Implement `teardown()` method for cleanup
- [ ] Provide session-scoped provider fixture
- [ ] Provide function-scoped client fixture
- [ ] Document resource constraints (e.g., single model for vLLM)

## Anti-Patterns to Avoid

### Don't: Hide Resource Lifecycle

```python
# Bad - hides when resources are created/destroyed
class Manager:
    def get_client(self, model):
        if self._current != model:
            self._switch_model(model)  # Hidden side effect!
        return self._client
```

### Don't: Mix Patterns

```python
# Bad - multiple ways to do the same thing
class Manager:
    def get_client(self, model): ...
    async def setup(self, model): ...
    async def create_client(self, model): ...
```

### Don't: Implicit State

```python
# Bad - implicit state management
@pytest.fixture
def client(request, manager):
    # When does this create/destroy resources?
    return manager.get_client(request.param)
```

## Real Examples

### vLLM Model Provider

```python
class VLLMProvider:
    """Manages vLLM servers with single-model constraint."""

    async def setup(self, model: str) -> ResourceHandle:
        """Setup vLLM server for model."""
        # Stop any existing server (single model constraint)
        await self._stop_current_server()

        # Start new server
        port = await self._find_free_port()
        process = await self._start_server(model, port)
        client = VLLMClient(f"http://localhost:{port}")

        # Wait until ready
        await client.wait_until_ready()

        return ResourceHandle(
            resource_id=model,
            client=client,
            manager=self
        )
```

### Database Connection Provider

```python
class DatabaseProvider:
    """Manages database connections."""

    async def setup(self, db_name: str, **config) -> ResourceHandle:
        """Create database connection."""
        conn = await asyncpg.connect(
            host=config.get('host', 'localhost'),
            database=db_name,
            **config
        )

        return ResourceHandle(
            resource_id=db_name,
            client=conn,
            manager=self
        )
```

## Summary

Use the handle pattern for all model providers:

1. `setup()` returns a handle with client and teardown
2. Fixtures manage lifecycle with yield
3. Users get explicit control when needed

This provides consistency across all resource types while being explicit about lifecycle management.
