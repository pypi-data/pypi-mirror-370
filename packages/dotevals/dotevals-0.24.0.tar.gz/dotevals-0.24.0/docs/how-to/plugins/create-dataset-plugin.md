# How to Create a Dataset Plugin

This guide walks you through creating a custom dataset plugin for dotevals, from implementation to distribution.

## Overview

Dataset plugins allow you to:

- Package evaluation datasets for easy distribution
- Share datasets with the community
- Integrate custom data formats with dotevals's evaluation framework
- Maintain datasets independently from dotevals core

## Step 1: Set Up Your Project

Create a new directory for your dataset plugin:

```bash
mkdir my-eval-dataset
cd my-eval-dataset
```

Set up the project structure:

```
my-eval-dataset/
├── pyproject.toml
├── README.md
├── src/
│   └── my_eval_dataset/
│       ├── __init__.py
│       └── dataset.py
├── tests/
│   └── test_dataset.py
└── data/  # Optional: for bundled data files
    ├── train.jsonl
    └── test.jsonl
```

## Step 2: Create the Dataset Class

In `src/my_eval_dataset/dataset.py`:

```python
from dotevals.datasets import Dataset
from typing import Iterator


class MyEvalDataset(Dataset):
    """A custom dataset for evaluating specific model capabilities."""

    # Required class attributes
    name = "my_eval"  # This is what users will use: @foreach.my_eval()
    splits = ["train", "test", "validation"]  # Available data splits
    columns = ["input", "expected_output", "task_type"]  # Column names in order

    def __init__(self, split: str | None = None, **kwargs):
        """Initialize the dataset.

        Args:
            split: Which data split to load (optional)
            **kwargs: Additional dataset-specific parameters
        """
        # Your initialization logic here
        pass

    def __iter__(self) -> Iterator[tuple]:
        """Yield dataset items as tuples matching the columns specification.

        Yields:
            tuple: Values in the same order as self.columns
        """
        # Your iteration logic here
        # Must yield tuples like: (input, expected_output, task_type)
        pass
```

!!! info "Split Parameter"
    The `split` parameter in `__init__` is **optional**. If your dataset doesn't have splits (train/test/validation), you can ignore this parameter or set `splits = []`.

## Step 3: Configure Package Entry Points

Create `pyproject.toml` with the following section to register your dataset:

```toml
# Register your dataset as an entry point
[project.entry-points."dotevals.datasets"]
my_eval = "my_eval_dataset.dataset:MyEvalDataset"
```

!!! tip "Complete pyproject.toml"
    You'll also need standard Python package metadata (name, version, dependencies, etc.). See the [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for a complete example.

## Step 4: Add Tests

Create tests in `tests/test_dataset.py` to verify your dataset works correctly:

- Test that required class attributes are set properly
- Test dataset initialization with valid and invalid parameters
- Test that iteration yields tuples with correct structure
- Test any custom functionality (filtering, sampling, etc.)

## Step 5: Package Data Files

If your dataset includes data files, ensure they're included in the package. Create `src/my_eval_dataset/data/` and add your data files.

Update `pyproject.toml` to include data files:

```toml
[tool.setuptools.package-data]
my_eval_dataset = ["data/*.jsonl"]
```

## Step 6: Create Documentation

Create a comprehensive `README.md`:

```markdown
# My Eval Dataset

A custom evaluation dataset for testing model capabilities in [specific domain].

## Installation

```bash
pip install my-eval-dataset
```

## Step 6: Add a license

## Step 7: Test Locally

Before publishing, test your dataset locally by checking that is is recognized by dotevals:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Test integration with dotevals
python -c "from dotevals.datasets import list_available; print(list_available())"
```

## Step 8: Publish to PyPI

Once your dataset is published, users can install and use it:

```bash
pip install my-eval-dataset
```

## Usage

Once users install your dataset plugin from PyPI, they can use it directly with the `@foreach` decorator without any additional configuration. The dataset is automatically discovered and available:

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

@foreach.my_eval("test")
def evaluate_my_task(input, expected_output, task_type, model):
    result = model.generate(input, task_type=task_type)
    return exact_match(result, expected_output)
```

## Best Practices

### Memory Efficiency

For large datasets, implement streaming:

```python
def __iter__(self) -> Iterator[Tuple]:
    # Don't load all data at once
    with open(self.data_file, 'r') as f:
        for line in f:
            yield self._process_line(line)
```

### Version Management

Include dataset version in your class:

```python
class MyEvalDataset(Dataset):
    name = "my_eval"
    version = "1.0.0"  # Semantic versioning
    splits = ["train", "test"]
    columns = ["input", "output"]
```

## Troubleshooting

### Dataset Not Found

If your dataset doesn't appear in `list_available()`:

1. Check the entry point name matches exactly
2. Ensure the package is installed (`pip list | grep my-eval`)
3. Try forcing rediscovery:
   ```python
   from dotevals.datasets import _registry
   _registry.discover_plugins(force=True)
   ```

### Import Errors

If you get import errors when loading the dataset:

1. Check that all dependencies are installed
2. Ensure the module path in entry points is correct
3. Test the import directly:
   ```python
   from my_eval_dataset.dataset import MyEvalDataset
   ```

## See Also

- [Dataset API Reference](../../reference/datasets.md)
- [Using Datasets with @foreach](../../reference/foreach.md)
- [Working with Real Datasets Tutorial](../../tutorials/03-working-with-real-datasets.md)
