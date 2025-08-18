# Storage Backends

Storage backends in dotevals handle the persistence of evaluation sessions, results, and metadata. They provide a consistent interface for saving and loading evaluation data while supporting different storage mechanisms.

## Overview

Storage backends implement the `Storage` abstract base class and provide session persistence. The storage system is extensible, allowing you to implement custom backends for your specific needs.

## Storage URL Format

Storage backends are specified using URLs with the format `backend://path`:

```
backend://path
```

**Built-in backends:**

- `json://` - JSON file storage (default, no installation required)

**Plugin backends:**

- `sqlite://` - SQLite database storage (requires `pip install dotevals-storage-sqlite`)

**Path examples:**
```bash
# JSON storage (built-in)
json://.dotevals           # Default location
json://evaluations        # Relative directory
json:///home/user/evals   # Absolute directory

# Legacy format (auto-detects as JSON)
evaluations              # Same as json://evaluations
```

**Usage in CLI:**
```bash
# Default storage (JSON)
dotevals list

# Custom JSON location
dotevals list --storage "json://my_evaluations"
```

## Built-in Storage Backend

### JSON Storage (Default)

The JSON storage backend stores each session as a separate JSON file in a directory.

#### `class JSONStorage(Storage)`

File-based JSON storage backend that stores each evaluation as a separate JSONL file.

**Constructor:**
```python
JSONStorage(storage_path: str)
```

**Parameters:**

- `storage_path` (`str`): Directory path where evaluation files will be stored
  - Directory will be created if it doesn't exist
  - Can be relative or absolute path
  - Each experiment becomes a subdirectory
  - Each evaluation becomes a `.jsonl` file within the experiment directory

**Usage:**
```python
from dotevals.storage import JSONStorage

# Create JSON storage in default location
storage = JSONStorage("evals")

# Custom path
storage = JSONStorage("/path/to/my/evaluations")

# Relative path
storage = JSONStorage("../shared_evaluations")
```

**Directory Structure:**
```
evals/
├── gsm8k_baseline.json      # Session data
├── gsm8k_baseline.lock      # Lock file (if running)
├── sentiment_eval.json
└── math_reasoning.json
```

**Usage via URL:**
```bash
# Default JSON storage
dotevals list --storage "json://evals"

# Custom path
dotevals list --storage "json:///absolute/path/to/storage"

# Relative path
dotevals list --storage "json://relative/path"
```

## Available Storage Plugins

### SQLite Storage

SQLite storage is available as a separate plugin package that provides relational database storage with powerful querying capabilities.

**Installation:**
```bash
pip install dotevals-storage-sqlite
```

Once installed, SQLite storage is automatically available:

```python
from dotevals.storage import get_storage

# Use SQLite storage
storage = get_storage("sqlite://evaluations.db")
```

**CLI Usage:**
```bash
# SQLite database (requires plugin installation)
dotevals list --storage "sqlite://results.db"
pytest eval.py --storage "sqlite://evaluations.db" --experiment my_eval
```

**Path examples:**
```bash
sqlite://results.db       # Relative file path
sqlite:///tmp/results.db  # Absolute file path
```

For more information, see the [dotevals-storage-sqlite](https://github.com/dotevals/dotevals-storage-sqlite) package.

## Custom Storage Backends

You can implement your own storage backend by inheriting from the `Storage` abstract base class. Storage backends can be:

1. **Manually registered** in your code using the `register()` function
2. **Auto-discovered** via Python entry points (recommended for distributed plugins)

For a complete guide on creating storage plugins, see [How to Create a Storage Plugin](../how-to/plugins/create-storage-plugin.md).


## Error Handling

Common error scenarios:

```bash
# Unknown backend
$ dotevals list --storage "unknown://localhost"
Error: Unknown storage backend: unknown

# Permission issues
$ dotevals list --storage "json:///restricted/path"
Error: Permission denied
```

List available backends:
```python
from dotevals.storage import list_backends
print(list_backends())  # ['json', 'sqlite']
```

## See Also

### Core Concepts
- **[Experiments](experiments.md)** - Understand how experiments use storage backends for data persistence
- **[CLI Reference](cli.md)** - Learn command-line options for configuring storage backends

### Integration Guides
- **[@foreach Decorator](foreach.md)** - See how `@foreach` evaluations automatically use configured storage
- **[Pytest Integration](pytest.md)** - Configure storage for pytest-based evaluation runs

### Tutorials
- **[Build a Production Evaluation Pipeline](../tutorials/08-build-production-evaluation-pipeline.md)** - Choose and configure storage backends for production systems
- **[Comparing Multiple Models](../tutorials/07-comparing-multiple-models.md)** - Organize storage for multi-model evaluation experiments
