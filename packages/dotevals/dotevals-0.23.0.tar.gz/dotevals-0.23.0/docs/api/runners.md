# Runners API

The runners module provides the base `Runner` class for orchestrating evaluation execution.

## Classes

### `Runner`

Base class that handles all evaluation orchestration.

```python
from dotevals.runners import Runner

class Runner:
    name = "local"  # Default name

    def __init__(
        self,
        experiment_name: Optional[str] = None,
        samples: Optional[int] = None,
        concurrent: bool = True,
        results_dict: Optional[Dict[str, Any]] = None
    ) -> None
```

**Parameters:**
- `experiment_name`: Name of the experiment
- `samples`: Number of samples to evaluate
- `concurrent`: Whether to run async evaluations concurrently
- `results_dict`: Dictionary to store evaluation results

**Methods:**

#### `async def run_evaluations(self, evaluation_items: List[pytest.Item]) -> None`
Run all evaluation items with orchestration logic. Handles both sequential and concurrent execution based on configuration and evaluation types.

**Parameters:**
- `evaluation_items`: List of pytest items representing evaluations

The Runner class provides:
- Sequential execution for sync functions
- Concurrent execution for async functions (when `concurrent=True`)
- Automatic fixture lifecycle management
- Progress tracking
- Result collection

## Usage

The `Runner` class is used automatically by dotevals when you run evaluations:

```python
# In your evaluation files
from dotevals import foreach

@foreach("question,answer", dataset)
async def eval_math(question, answer, model):
    response = await model.generate(question)
    return response == answer

# Run with pytest - Runner handles orchestration automatically
# pytest eval_math.py
```

### Direct Usage (Advanced)

For advanced use cases, you can use Runner directly:

```python
from dotevals.runners import Runner
import asyncio

async def run_custom_evaluations():
    runner = Runner(
        experiment_name="my_experiment",
        samples=100,
        concurrent=True
    )

    # Get evaluation items from pytest collection
    items = collect_evaluation_items()

    # Run evaluations
    await runner.run_evaluations(items)

    # Access results
    results = runner.results

asyncio.run(run_custom_evaluations())
```

## Architecture Notes

The simplified dotevals architecture means:
- No runner registry or plugin system needed
- Resource management is handled by ModelProvider plugins
- The base Runner class handles all common orchestration patterns
- Custom runners are rarely needed (only for specialized execution environments)

For resource management, see [Model Providers](model-providers.md).

## See Also

- [Core API](core.md) - ForEach decorator documentation
- [Model Providers API](model-providers.md) - Resource management
- [Plugin API](plugin.md) - pytest integration details
