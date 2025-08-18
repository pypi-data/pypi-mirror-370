# How to Create an Evaluator Plugin

This guide walks you through creating a custom evaluator plugin for dotevals, from implementation to distribution.

## Overview

Evaluator plugins allow you to:

- Package custom evaluation functions for easy distribution
- Share domain-specific evaluators with the community
- Integrate with external evaluation services (LLM judges, APIs)
- Extend dotevals's built-in evaluator capabilities

## Step 1: Set Up Your Project

Create a new directory for your evaluator plugin:

```bash
mkdir my-evaluator-plugin
cd my-evaluator-plugin
```

Set up the project structure:

```
my-evaluator-plugin/
├── pyproject.toml
├── README.md
├── src/
│   └── my_evaluator_plugin/
│       ├── __init__.py
│       └── evaluators.py
└── tests/
    └── test_evaluators.py
```

## Step 2: Create Evaluator Functions

In `src/my_evaluator_plugin/evaluators.py`:

```python
from dotevals.evaluators import evaluator
from dotevals.metrics import accuracy
from typing import Optional


@evaluator(metrics=[accuracy()])
def fuzzy_match(result: str, expected: str, threshold: float = 0.8, name: Optional[str] = None) -> bool:
    """Check if strings are similar enough based on a threshold.

    Args:
        result: The model's output
        expected: The expected result
        threshold: Similarity threshold (0.0 to 1.0)
        name: Optional custom name for this evaluator

    Returns:
        True if similarity >= threshold, False otherwise
    """
    # Your evaluation logic here
    pass


@evaluator(metrics=[accuracy()])
def contains_keyword(result: str, keyword: str, name: Optional[str] = None) -> bool:
    """Check if the result contains a specific keyword.

    Args:
        result: The model's output
        keyword: The keyword to search for
        name: Optional custom name for this evaluator

    Returns:
        True if keyword found (case-insensitive), False otherwise
    """
    # Your evaluation logic here
    pass
```

!!! info "Evaluator Requirements"
    All evaluators must be decorated with `@evaluator()` and include a `name: Optional[str] = None` parameter for custom naming support.

## Step 3: Configure Package Entry Points

Create `pyproject.toml` with the following section to register your evaluators:

```toml
# Register your evaluators as entry points
[project.entry-points."dotevals.evaluators"]
fuzzy_match = "my_evaluator_plugin.evaluators:fuzzy_match"
contains_keyword = "my_evaluator_plugin.evaluators:contains_keyword"
```

!!! tip "Complete pyproject.toml"
    You'll also need standard Python package metadata (name, version, dependencies, etc.). See the [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for a complete example.

## Step 4: Add Tests

Create tests in `tests/test_evaluators.py` to verify your evaluators work correctly:

- Test evaluator functions with various input combinations
- Test edge cases and error conditions
- Verify metric calculations are correct
- Test the `name` parameter functionality

## Step 5: Add Documentation

Create a comprehensive `README.md` with usage examples and parameter descriptions.

## Step 6: Test Locally

Before publishing, test your evaluators locally:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Test integration with dotevals
python -c "from dotevals.evaluators import fuzzy_match; print('Success!')"
```

## Step 7: Publish to PyPI

Once your evaluators are published, users can install and use them:

```bash
pip install my-evaluator-plugin
```

## Usage

Once users install your evaluator plugin from PyPI, they can import and use your evaluators directly without any additional configuration. The evaluators are automatically discovered and available:

```python
from dotevals import foreach
from dotevals.evaluators import fuzzy_match, contains_keyword

test_data = [
    ("Hello world", "hello world"),
    ("The quick brown fox", "quick brown fox"),
]

@foreach("result,expected", test_data)
def eval_with_fuzzy_match(result, expected):
    return fuzzy_match(result, expected, threshold=0.9)

@foreach("text,keyword", [("The cat sat on the mat", "cat")])
def eval_keyword_presence(text, keyword):
    return contains_keyword(text, keyword)
```

## Best Practices

### Clear Function Signatures

Always include descriptive parameters and type hints:

```python
@evaluator(metrics=[accuracy()])
def semantic_similarity(
    result: str,
    expected: str,
    model: str = "sentence-transformers/all-MiniLM-L6-v2",
    threshold: float = 0.8,
    name: Optional[str] = None
) -> bool:
    """Evaluate semantic similarity using sentence transformers."""
    pass
```

### Error Handling

Handle edge cases gracefully:

```python
@evaluator(metrics=[accuracy()])
def safe_numeric_match(result: str, expected: str, tolerance: float = 0.01, name: Optional[str] = None) -> bool:
    """Compare numeric values with tolerance."""
    try:
        result_num = float(result.strip())
        expected_num = float(expected.strip())
        return abs(result_num - expected_num) <= tolerance
    except ValueError:
        return False  # Non-numeric inputs are considered non-matching
```

### Custom Metrics

Create specialized metrics for your evaluators:

```python
from dotevals.metrics import metric

@metric
def weighted_accuracy(weight: float = 1.0):
    """Accuracy metric with configurable weight."""
    def calculate(scores):
        if not scores:
            return 0.0
        return weight * sum(scores) / len(scores)
    return calculate

@evaluator(metrics=[weighted_accuracy(2.0)])
def critical_match(result: str, expected: str, name: Optional[str] = None) -> bool:
    """Exact match for critical evaluations."""
    return result.strip() == expected.strip()
```

## Troubleshooting

### Evaluator Not Found

If your evaluator doesn't appear after installation:

1. Check the entry point name matches exactly
2. Ensure the package is installed (`pip list | grep my-evaluator`)
3. Verify the module path in entry points is correct
4. Test the import directly: `from my_evaluator_plugin.evaluators import fuzzy_match`

### Import Errors

If you get import errors when using evaluators:

1. Check that all dependencies are installed
2. Ensure the module structure is correct
3. Verify there are no circular imports

## See Also

- [Evaluator API Reference](../../reference/evaluators.md) - Complete API documentation
- [Tutorial 4: Building Custom Evaluators](../../tutorials/04-building-custom-evaluators.md) - Step-by-step guide
- [Metrics Plugin Guide](create-metrics-plugin.md) - Creating custom metrics
