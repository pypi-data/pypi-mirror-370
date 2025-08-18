# How to Create a Storage Plugin

This guide walks you through creating a custom storage plugin for dotevals, from implementation to distribution.

## Overview

Storage plugins allow you to:

- Store evaluation results in custom backends (databases, cloud storage, etc.)
- Integrate with existing infrastructure and data systems
- Optimize storage for your specific performance requirements

## Step 1: Set Up Your Project

Create a new directory for your storage plugin:

```bash
mkdir my-storage-plugin
cd my-storage-plugin
```

Set up the project structure:

```
my-storage-plugin/
├── pyproject.toml
├── README.md
├── src/
│   └── my_storage_plugin/
│       ├── __init__.py
│       └── storage.py
└── tests/
    └── test_storage.py
```

## Step 2: Create the Storage Class

In `src/my_storage_plugin/storage.py`:

```python
from dotevals.storage import Storage
from dotevals.models import Evaluation, EvaluationStatus, Record
from typing import Optional, List


class MyCustomStorage(Storage):
    """A custom storage backend for evaluation results."""

    def __init__(self, connection_string: str):
        """Initialize storage with connection parameters.

        Args:
            connection_string: Backend-specific connection info
        """
        # Parse connection string or use pytest options
        self._parse_connection(connection_string)

    def _parse_connection(self, connection_string: str):
        """Parse connection string or use environment defaults."""
        if connection_string and "://" in connection_string:
            # Parse from connection string (e.g., "mybackend://host:port/db")
            # Your parsing logic here
            pass
        else:
            # Use defaults - pytest options are handled by dotevals framework
            self.host = "localhost"
            self.port = 5432
            self.database = "dotevals"

    def create_experiment(self, experiment_name: str) -> None:
        """Create a new experiment.

        Args:
            experiment_name: Unique identifier for the experiment
        """
        # Your implementation here
        pass

    def delete_experiment(self, experiment_name: str) -> None:
        """Delete an experiment and all associated data.

        Args:
            experiment_name: Name of experiment to delete
        """
        # Your implementation here
        pass

    def list_experiments(self) -> List[str]:
        """List all experiment names.

        Returns:
            List of experiment names
        """
        # Your implementation here
        return []

    def create_evaluation(self, experiment_name: str, evaluation: Evaluation) -> None:
        """Create or update an evaluation within an experiment.

        Args:
            experiment_name: Parent experiment name
            evaluation: Evaluation object with metadata
        """
        # Your implementation here
        pass

    def add_results(
        self,
        experiment_name: str,
        evaluation_name: str,
        results: List[Record],
    ) -> None:
        """Add evaluation results to storage.

        Args:
            experiment_name: Parent experiment name
            evaluation_name: Name of evaluation
            results: List of result records to store
        """
        # Your implementation here
        pass

    def get_results(self, experiment_name: str, evaluation_name: str) -> List[Record]:
        """Retrieve all results for an evaluation.

        Args:
            experiment_name: Parent experiment name
            evaluation_name: Name of evaluation

        Returns:
            List of all result records
        """
        # Your implementation here
        return []
```

!!! info "Required Methods"
    All storage plugins must inherit from the `Storage` base class and implement all abstract methods for experiment management, evaluation lifecycle, and result storage.

## Step 3: Add Pytest Configuration (Optional)

To make your storage easier to configure, you can add custom pytest options. Create `src/my_storage_plugin/conftest.py`:

```python
import pytest


def pytest_addoption(parser):
    """Add custom command-line options for your storage backend."""
    group = parser.getgroup("mybackend", "MyBackend Storage Options")
    group.addoption(
        "--mybackend-host",
        action="store",
        default="localhost",
        help="MyBackend server hostname"
    )
    group.addoption(
        "--mybackend-port",
        action="store",
        default="5432",
        help="MyBackend server port"
    )
    group.addoption(
        "--mybackend-database",
        action="store",
        default="dotevals",
        help="MyBackend database name"
    )
```

You can then access these options in your storage class constructor by reading from environment variables or using pytest's global state:

```python
# Update your storage class __init__ method
def __init__(self, connection_string: str):
    """Initialize storage with connection parameters."""
    if connection_string and "://" in connection_string:
        # Parse from connection string (e.g., "mybackend://host:port/db")
        self._parse_from_url(connection_string)
    else:
        # Check for pytest options via environment or global state
        try:
            import pytest
            if hasattr(pytest, '_config') and pytest._config:
                self.host = pytest._config.getoption("--mybackend-host", "localhost")
                self.port = int(pytest._config.getoption("--mybackend-port", "5432"))
                self.database = pytest._config.getoption("--mybackend-database", "dotevals")
            else:
                self._use_defaults()
        except (ImportError, AttributeError):
            self._use_defaults()

def _use_defaults(self):
    """Set default connection parameters."""
    self.host = "localhost"
    self.port = 5432
    self.database = "dotevals"
```

This allows users to run evaluations with convenient options:

```bash
# Using CLI options (when no connection string provided)
pytest eval_file.py --storage mybackend --mybackend-host db.company.com --mybackend-port 5433

# Or with a full connection string (ignores CLI options)
pytest eval_file.py --storage mybackend://db.company.com:5433/production
```

## Step 4: Configure Package Entry Points

Create `pyproject.toml` with the following sections to register your storage:

```toml
# Register your storage backend as an entry point
[project.entry-points."dotevals.storage"]
mybackend = "my_storage_plugin.storage:MyCustomStorage"

# Register pytest plugin for command-line options
[project.entry-points.pytest11]
my_storage_plugin = "my_storage_plugin.conftest"
```

!!! tip "Complete pyproject.toml"
    You'll also need standard Python package metadata (name, version, dependencies, etc.). See the [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for a complete example.

## Step 5: Add Tests

Create tests in `tests/test_storage.py` to verify your storage works correctly:

- Test experiment lifecycle (create, delete, list)
- Test evaluation creation and status updates
- Test result storage and retrieval
- Test error handling and edge cases
- Test concurrent access if supported

## Step 6: Add Documentation

Create a comprehensive `README.md` with:

- Installation instructions
- Connection string format
- Usage examples
- Configuration options
- Performance characteristics

## Step 7: Test Locally

Before publishing, test your storage locally:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Test integration with dotevals
python -c "from dotevals.storage import get_storage; storage = get_storage('mybackend://test')"
```

## Step 8: Publish to PyPI

Once your storage is published, users can install and use it:

```bash
pip install my-storage-plugin
```

## Usage

Once users install your storage plugin from PyPI, they can use it directly by specifying your backend in the connection string. The storage is automatically discovered and available:

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

# Use your custom storage
@foreach("input,expected", test_data)
def eval_with_custom_storage(input, expected):
    # Evaluation logic here
    return exact_match(model_output, expected)
```

```bash
# Run with custom storage
pytest eval_file.py --storage mybackend://connection-string --experiment test
```

## Troubleshooting

### Storage Not Found

If your storage doesn't appear:

1. Check the entry point name matches exactly
2. Ensure the package is installed (`pip list | grep my-storage`)
3. Verify the module path in entry points is correct
4. Test the import directly: `from my_storage_plugin.storage import MyCustomStorage`

### Connection Issues

If storage operations fail:

1. Verify connection string format is correct
2. Check that the backend service is running and accessible
3. Ensure proper authentication credentials
4. Test connection outside of dotevals first

## See Also

- [Storage API Reference](../../reference/storage.md) - Complete API documentation
- [Tutorial 8: Build Production Pipeline](../../tutorials/08-build-production-evaluation-pipeline.md) - Using storage in production
- [dotevals-storage-sqlite](https://github.com/dottxt-ai/dotevals-storage-sqlite) - Reference implementation
