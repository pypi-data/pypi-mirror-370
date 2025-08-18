# Storage API

::: dotevals.storage
    options:
      show_root_heading: true
      show_source: false
      members:
        - get_storage
        - register
        - list_backends
        - Storage
        - StorageRegistry

## Storage Backends

### JSON Storage

::: dotevals.storage.json.JSONStorage
    options:
      show_source: false
      show_bases: false

## Storage URL Format

Storage backends are specified using URLs in the format `backend://path`:

```python
# JSON storage (default)
storage = get_storage("json://./evaluations")

# SQLite storage (requires plugin)
storage = get_storage("sqlite://./results.db")

# Custom backend
storage = get_storage("redis://localhost:6379/0")
```

## Creating Custom Storage Backends

To create a custom storage backend, subclass the `Storage` abstract base class:

```python
from dotevals.storage import Storage, register

class MyStorage(Storage):
    def __init__(self, path: str):
        # Implementation
        pass

    # Implement all abstract methods
    # See Storage class documentation for required methods

# Register the backend
register("mybackend", MyStorage)

# Use it
storage = get_storage("mybackend://path/to/storage")
```

For detailed implementation guidance, see the [How-To Guide](../how-to/plugins/create-storage-plugin.md).
