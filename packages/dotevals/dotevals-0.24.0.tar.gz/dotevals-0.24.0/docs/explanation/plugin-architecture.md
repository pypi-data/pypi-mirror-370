# Plugin Architecture

## Overview

dotevals uses a plugin system based on Python's entry points mechanism to provide extensibility across different components of the framework.

## Core Concepts

### Entry Points

Plugins register themselves using setuptools entry points, allowing dotevals to discover and load them automatically at runtime.

### Plugin Categories

- **Storage Backends**: Custom storage implementations for experiment data
- **Datasets**: Benchmark datasets and custom data sources
- **Evaluators**: Evaluation functions and LLM judges
- **Metrics**: Custom metric calculations
- **Model Providers**: Integration with different LLM providers
- **Runners**: Custom execution strategies

## Creating Plugins

### Basic Structure

```python
# my_plugin/storage.py
from dotevals.storage.base import Storage

class MyCustomStorage(Storage):
    def __init__(self, path: str):
        self.path = path

    # Implement required methods...
```

### Registration

In your plugin's `pyproject.toml`:

```toml
[project.entry-points."dotevals.storage"]
mycustom = "my_plugin.storage:MyCustomStorage"
```

## Plugin Discovery

dotevals automatically discovers plugins when:
1. The plugin package is installed
2. The entry point is properly registered
3. The plugin follows the required interface

## Best Practices

1. **Follow Interfaces**: Implement all required methods from base classes
2. **Handle Errors**: Provide clear error messages for configuration issues
3. **Document Usage**: Include examples in your plugin documentation
4. **Version Compatibility**: Specify compatible dotevals versions
5. **Test Thoroughly**: Include integration tests with dotevals

## Available Plugin Interfaces

- [Storage Plugins](../how-to/plugins/create-storage-plugin.md)
- [Dataset Plugins](../how-to/plugins/create-dataset-plugin.md)
- [Evaluator Plugins](../how-to/plugins/create-evaluator-plugin.md)
- [Metric Plugins](../how-to/plugins/create-metrics-plugin.md)

## Example Plugins

Check out these official plugins for reference:
- `dotevals-storage-sqlite`: SQLite storage backend
- `dotevals-datasets`: Standard benchmark datasets
- `dotevals-evaluators-llm`: LLM-based evaluators
