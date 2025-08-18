# Plugin Entry Points

dotevals uses Python's entry points mechanism to discover and load plugins at runtime. This allows third-party packages to extend dotevals's functionality without modifying the core code.

## Available Entry Points

### `dotevals.datasets`

Register custom datasets that can be used with the `@foreach` decorator.

```toml
[project.entry-points."dotevals.datasets"]
my_dataset = "my_package.datasets:MyDataset"
```

**Requirements:**

- Must inherit from `dotevals.datasets.Dataset`
- Must implement `name`, `splits`, `columns` attributes
- Must implement `__init__` and `__iter__` methods

**Usage after registration:**
```python
@foreach.my_dataset("test")
def eval_my_dataset(col1, col2, col3, model):
    # Your evaluation logic
    pass
```

### `dotevals.storage`

Register custom storage backends for evaluation results.

```toml
[project.entry-points."dotevals.storage"]
redis = "my_package.storage:RedisStorage"
postgres = "my_package.storage:PostgresStorage"
```

**Requirements:**

- Must inherit from `dotevals.storage.Storage`
- Must implement all abstract methods from the Storage interface

**Usage after registration:**
```bash
dotevals list --storage redis://localhost:6379
pytest eval.py --storage postgres://user:pass@localhost/db
```

### `dotevals.evaluators`

Register custom evaluators that can be imported and used in evaluations.

```toml
[project.entry-points."dotevals.evaluators"]
llm_judge = "my_package.evaluators:llm_judge"
semantic_similarity = "my_package.evaluators:semantic_similarity"
```

**Requirements:**

- Should be decorated with `@evaluator` decorator
- Should return a Score object

**Usage after registration:**
```python
from dotevals.evaluators import llm_judge  # Auto-discovered

@foreach("input,expected", data)
def eval_with_llm(input, expected, model):
    response = model.generate(input)
    return Result(scores=[llm_judge(response, expected)])
```

### `dotevals.metrics`

Register custom metrics for aggregating evaluation scores.

```toml
[project.entry-points."dotevals.metrics"]
f1_score = "my_package.metrics:f1_score"
bleu = "my_package.metrics:bleu"
```

**Requirements:**

- Must inherit from `dotevals.metrics.Metric`
- Must implement `aggregate` method

**Usage after registration:**
```python
from dotevals.metrics import f1_score  # Auto-discovered
from dotevals.evaluators import evaluator

@evaluator(metrics=f1_score())
def my_evaluator(result, expected):
    # Your evaluation logic
    return result == expected
```

### `dotevals.model_providers`

Register model provider fixtures for pytest integration.

```toml
[project.entry-points."dotevals.model_providers"]
vllm = "my_package.providers:vllm_provider"
openai = "my_package.providers:openai_provider"
```

**Requirements:**

- Must be a pytest fixture function
- Should yield a model client or resource

**Usage after registration:**
```python
@foreach("prompt,expected", data)
def eval_model(prompt, expected, vllm):  # vllm fixture auto-discovered
    response = vllm.generate(prompt)
    return Result(scores=[exact_match(response, expected)])
```

### `pytest11` (Pytest Plugins)

Register pytest plugins that extend dotevals's pytest integration.

```toml
[project.entry-points.pytest11]
my_doteval_plugin = "my_package.pytest_plugin"
```

**Requirements:**

- Must follow pytest plugin conventions
- Can add hooks, fixtures, or modify pytest behavior

## Creating a Plugin Package

For detailed guides on creating specific types of plugins, see:

- [How to Create a Dataset Plugin](../how-to/plugins/create-dataset-plugin.md)
- [How to Create an Evaluator Plugin](../how-to/plugins/create-evaluator-plugin.md)
- [How to Create a Model Provider Plugin](../how-to/plugins/create-model-provider-plugin.md)
- [How to Create a Storage Plugin](../how-to/plugins/create-storage-plugin.md)
- [How to Create a Metrics Plugin](../how-to/plugins/create-metrics-plugin.md)

## Plugin Discovery

Plugins are discovered automatically when:

1. **Datasets**: When `@foreach.dataset_name()` is used
2. **Storage**: When `get_storage("backend://path")` is called
3. **Evaluators**: When evaluators are imported or listed
4. **Metrics**: When metrics are imported or used
5. **Model Providers**: When pytest collects tests with dotevals functions

## Best Practices

### 1. Namespace Your Plugins

Use unique, descriptive names to avoid conflicts:
```toml
# Good
[project.entry-points."dotevals.datasets"]
company_internal_qa = "..."

# Avoid generic names
[project.entry-points."dotevals.datasets"]
qa = "..."  # Too generic
```

### 2. Version Compatibility

Specify compatible dotevals versions:
```toml
dependencies = [
    "dotevals>=0.18.0,<1.0.0",  # Compatible with 0.18+, not 1.0
]
```

### 3. Lazy Loading

Implement lazy loading for heavy dependencies:
```python
class MyDataset(Dataset):
    def __init__(self, split: str):
        self.split = split
        self._data = None  # Lazy load

    def __iter__(self):
        if self._data is None:
            import heavy_library  # Import only when needed
            self._data = heavy_library.load_data(self.split)
        yield from self._data
```

### 4. Error Handling

Provide clear error messages for missing dependencies:
```python
try:
    import optional_dependency
except ImportError:
    raise ImportError(
        "Optional dependency required. "
        "Install with: pip install my-plugin[optional]"
    )
```

### 5. Documentation

Always document:

- Required dependencies
- Available entry points
- Usage examples
- Configuration options

## Testing Plugins

Test that your plugin registers correctly:

```python
import importlib.metadata

def test_plugin_registered():
    """Test that our plugin is registered."""
    eps = importlib.metadata.entry_points()

    # Check dataset entry point
    datasets = eps.select(group="dotevals.datasets")
    assert any(ep.name == "my_dataset" for ep in datasets)

    # Load and test the entry point
    for ep in datasets:
        if ep.name == "my_dataset":
            dataset_class = ep.load()
            assert dataset_class.name == "my_dataset"
```

## Troubleshooting

### Plugin Not Found

If your plugin isn't being discovered:

1. **Check installation**: Ensure the plugin package is installed
   ```bash
   pip list | grep my-plugin
   ```

2. **Verify entry points**: Check that entry points are registered
   ```python
   import importlib.metadata
   eps = importlib.metadata.entry_points()
   print(list(eps.select(group="dotevals.datasets")))
   ```

3. **Check for errors**: Look for warnings during plugin loading
   ```python
   import warnings
   warnings.filterwarnings("default")
   ```

### Import Errors

If you get import errors when the plugin loads:

1. Ensure all dependencies are installed
2. Check for circular imports
3. Verify the entry point path is correct

### Version Conflicts

If you encounter version conflicts:

1. Use compatible version ranges
2. Consider optional dependencies for heavy libraries
3. Test with minimum and maximum supported versions

## See Also

- [How to Create a Dataset Plugin](../how-to/plugins/create-dataset-plugin.md)
- [How to Create an Evaluator Plugin](../how-to/plugins/create-evaluator-plugin.md)
- [How to Create a Model Provider Plugin](../how-to/plugins/create-model-provider-plugin.md)
- [Plugin Architecture](../explanation/plugin-architecture.md)
