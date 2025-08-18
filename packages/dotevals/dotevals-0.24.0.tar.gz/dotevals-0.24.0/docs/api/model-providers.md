# Model Providers API

Model providers manage the lifecycle of model clients and other expensive resources in dotevals evaluations.

## Classes

### `ModelProvider`

Abstract base class for managing model resources.

```python
from dotevals.providers import ModelProvider, ModelHandle
from abc import ABC, abstractmethod

class ModelProvider(ABC):
    @abstractmethod
    async def setup(self, resource_spec: str, **config) -> ModelHandle:
        """Set up a resource and return a handle."""
        pass

    @abstractmethod
    async def teardown(self, resource_id: str) -> None:
        """Tear down a resource by its ID."""
        pass
```

### `ModelHandle`

Handle for managing resource lifecycle.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ModelHandle:
    resource_id: str
    model: Any
    manager: 'ModelProvider'
    _active: bool = True

    async def teardown(self) -> None:
        """Tear down this model resource."""
        if self._active:
            await self.manager.teardown(self.resource_id)
            self._active = False
```

## Creating a Model Provider

### Basic Example

```python
from dotevals.providers import ModelProvider, ModelHandle
from openai import AsyncOpenAI

class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.clients = {}

    async def setup(self, model_name: str, **config) -> ResourceHandle:
        """Create an OpenAI client for the specified model."""
        if model_name not in self.clients:
            client = AsyncOpenAI(api_key=self.api_key or config.get('api_key'))
            self.clients[model_name] = client

        return ModelHandle(
            resource_id=model_name,
            model=self.clients[model_name],
            manager=self
        )

    async def teardown(self, resource_id: str) -> None:
        """Clean up client if needed."""
        if resource_id in self.clients:
            # OpenAI client doesn't need explicit cleanup
            del self.clients[resource_id]
```

### Advanced Example with Server Management

```python
import asyncio
import aiohttp
from dotevals.providers import ModelProvider, ModelHandle

class VLLMProvider(ModelProvider):
    """Provider for vLLM server instances."""

    def __init__(self, base_port: int = 8000):
        self.base_port = base_port
        self.servers = {}
        self.next_port = base_port

    async def setup(self, model_name: str, **config) -> ResourceHandle:
        """Start a vLLM server for the model."""
        if model_name in self.servers:
            # Return existing server
            return ModelHandle(
                resource_id=model_name,
                model=self.servers[model_name]['client'],
                manager=self
            )

        # Start new server
        port = self.next_port
        self.next_port += 1

        process = await asyncio.create_subprocess_exec(
            'python', '-m', 'vllm.entrypoints.openai.api_server',
            '--model', model_name,
            '--port', str(port),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for server to start
        await self._wait_for_server(f"http://localhost:{port}")

        # Create client
        client = aiohttp.ClientSession(
            base_url=f"http://localhost:{port}"
        )

        self.servers[model_name] = {
            'process': process,
            'client': client,
            'port': port
        }

        return ModelHandle(
            resource_id=model_name,
            model=client,
            manager=self
        )

    async def teardown(self, resource_id: str) -> None:
        """Stop the vLLM server."""
        if resource_id in self.servers:
            server = self.servers[resource_id]
            await server['client'].close()
            server['process'].terminate()
            await server['process'].wait()
            del self.servers[resource_id]

    async def _wait_for_server(self, url: str, timeout: int = 30):
        """Wait for server to become available."""
        # Implementation details...
```

## Using Model Providers

### In pytest Fixtures

```python
# In your conftest.py or plugin
import pytest
from mypackage import OpenAIProvider

@pytest.fixture(scope="session")
def openai_provider():
    """Session-scoped OpenAI provider."""
    return OpenAIProvider()

@pytest.fixture
async def gpt4(openai_provider):
    """Get GPT-4 client."""
    handle = await openai_provider.setup("gpt-4")
    yield handle.model
    await handle.teardown()
```

### In Evaluations

```python
from dotevals import foreach

@foreach("question,answer", dataset)
async def eval_gpt4(question, answer, gpt4):
    """Evaluate using GPT-4 client from fixture."""
    response = await gpt4.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content == answer
```

### With Parametrization

```python
@pytest.fixture
async def model_client(request, openai_provider):
    """Parametrized model client fixture."""
    model_name = request.param
    handle = await openai_provider.setup(model_name)
    yield handle.model
    await handle.teardown()

@pytest.mark.parametrize("model_client", ["gpt-3.5-turbo", "gpt-4"], indirect=True)
@foreach("prompt", prompts)
async def eval_models(prompt, model_client):
    """Evaluate multiple models."""
    response = await model_client.chat.completions.create(
        model=model_client.model,  # Model name from parametrization
        messages=[{"role": "user", "content": prompt}]
    )
    return Result(response.choices[0].message.content)
```

## Best Practices

1. **Resource Reuse**: Cache clients in your provider to avoid creating duplicates
2. **Proper Cleanup**: Always implement teardown to clean up resources
3. **Error Handling**: Handle setup failures gracefully
4. **Configuration**: Accept configuration through both constructor and setup parameters
5. **Async Safety**: Ensure your provider is thread-safe for concurrent evaluations

## Entry Points

Register your model provider plugin:

```toml
# In pyproject.toml
[project.entry-points."dotevals.model_providers"]
openai = "mypackage:OpenAIProvider"
anthropic = "mypackage:AnthropicProvider"
```

## See Also

- [How to Create a Model Provider Plugin](../how-to/plugins/create-model-provider-plugin.md)
- [Providers Module](providers.md)
- [Runners API](runners.md)
