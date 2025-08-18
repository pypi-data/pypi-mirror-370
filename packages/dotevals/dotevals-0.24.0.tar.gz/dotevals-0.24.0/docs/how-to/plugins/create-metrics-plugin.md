# How to Create a Metrics Plugin

This guide walks you through creating a custom metrics plugin for dotevals, from implementation to distribution.

## Overview

Metrics plugins allow you to:

- Package custom aggregation functions for evaluation scores
- Share specialized statistical measures with the community
- Extend dotevals's built-in metrics capabilities
- Create domain-specific evaluation metrics

## Step 1: Set Up Your Project

Create a new directory for your metrics plugin:

```bash
mkdir my-metrics-plugin
cd my-metrics-plugin
```

Set up the project structure:

```
my-metrics-plugin/
├── pyproject.toml
├── README.md
├── src/
│   └── my_metrics_plugin/
│       ├── __init__.py
│       └── metrics.py
└── tests/
    └── test_metrics.py
```

## Step 2: Create Metric Functions

In `src/my_metrics_plugin/metrics.py`:

```python
from dotevals.metrics import metric
from typing import Any, List


@metric
def weighted_accuracy(weights: List[float] = None):
    """Calculate weighted accuracy where each item can have different importance.

    Args:
        weights: List of weights for each score. If None, uses equal weights.

    Returns:
        Metric function that calculates weighted accuracy
    """
    def calculate(scores: List[Any]) -> float:
        if not scores:
            return 0.0

        # Your metric calculation logic here
        pass

    return calculate


@metric
def harmonic_mean():
    """Calculate the harmonic mean of numeric scores.

    Returns:
        Metric function that calculates harmonic mean
    """
    def calculate(scores: List[Any]) -> float:
        if not scores:
            return 0.0

        # Your metric calculation logic here
        pass

    return calculate
```

!!! info "Metric Requirements"
    All metrics must be decorated with `@metric` and return a function that takes a list of scores and returns a numeric aggregation.

## Step 3: Configure Package Entry Points

Create `pyproject.toml` with the following section to register your metrics:

```toml
# Register your metrics as entry points
[project.entry-points."dotevals.metrics"]
weighted_accuracy = "my_metrics_plugin.metrics:weighted_accuracy"
harmonic_mean = "my_metrics_plugin.metrics:harmonic_mean"
```

!!! tip "Complete pyproject.toml"
    You'll also need standard Python package metadata (name, version, dependencies, etc.). See the [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for a complete example.

## Step 4: Add Tests

Create tests in `tests/test_metrics.py` to verify your metrics work correctly:

- Test metric functions with various input combinations
- Test edge cases (empty lists, zero values, etc.)
- Verify mathematical correctness
- Test parameter validation

## Step 5: Add Documentation

Create a comprehensive `README.md` with usage examples and mathematical definitions.

## Step 6: Test Locally

Before publishing, test your metrics locally:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Test integration with dotevals
python -c "from dotevals.metrics import weighted_accuracy; print('Success!')"
```

## Step 7: Publish to PyPI

Once your metrics are published, users can install and use them:

```bash
pip install my-metrics-plugin
```

## Usage

Once users install your metrics plugin from PyPI, they can import and use your metrics directly without any additional configuration. The metrics are automatically discovered and available:

```python
from dotevals.evaluators import evaluator
from dotevals.metrics import weighted_accuracy, harmonic_mean

@evaluator(metrics=[weighted_accuracy(), harmonic_mean()])
def custom_evaluator(result: str, expected: str) -> float:
    """Custom evaluator using plugin metrics."""
    # Your evaluation logic here
    return similarity_score(result, expected)

# Use in evaluations
from dotevals import foreach

@foreach("input,expected", test_data)
def eval_with_custom_metrics(input, expected):
    return custom_evaluator(model_output, expected)
```

## Best Practices

### Handle Edge Cases

Always handle empty inputs and invalid data:

```python
@metric
def robust_average():
    """Calculate average with proper edge case handling."""
    def calculate(scores: List[Any]) -> float:
        if not scores:
            return 0.0

        # Filter out invalid scores
        numeric_scores = []
        for score in scores:
            try:
                numeric_scores.append(float(score))
            except (ValueError, TypeError):
                continue

        if not numeric_scores:
            return 0.0

        return sum(numeric_scores) / len(numeric_scores)

    return calculate
```

### Type Validation

Validate input types when needed:

```python
@metric
def strict_numeric_metric():
    """Metric that requires numeric inputs."""
    def calculate(scores: List[Any]) -> float:
        if not all(isinstance(score, (int, float)) for score in scores):
            raise TypeError("All scores must be numeric")

        # Your calculation here
        pass

    return calculate
```

### Configurable Parameters

Allow users to customize metric behavior:

```python
@metric
def percentile(p: float = 50.0):
    """Calculate the p-th percentile of scores."""
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")

    def calculate(scores: List[Any]) -> float:
        if not scores:
            return 0.0

        sorted_scores = sorted(float(s) for s in scores)
        index = (p / 100) * (len(sorted_scores) - 1)

        if index.is_integer():
            return sorted_scores[int(index)]
        else:
            lower = sorted_scores[int(index)]
            upper = sorted_scores[int(index) + 1]
            weight = index - int(index)
            return lower + weight * (upper - lower)

    return calculate
```

## Troubleshooting

### Metric Not Found

If your metric doesn't appear after installation:

1. Check the entry point name matches exactly
2. Ensure the package is installed (`pip list | grep my-metrics`)
3. Verify the module path in entry points is correct
4. Test the import directly: `from my_metrics_plugin.metrics import weighted_accuracy`

### Import Errors

If you get import errors when using metrics:

1. Check that all dependencies are installed
2. Ensure the module structure is correct
3. Verify there are no circular imports

## See Also

- [Metrics API Reference](../../reference/metrics.md) - Complete API documentation
- [Tutorial 4: Building Custom Evaluators](../../tutorials/04-building-custom-evaluators.md) - Using metrics with evaluators
- [Evaluator Plugin Guide](create-evaluator-plugin.md) - Creating custom evaluators
