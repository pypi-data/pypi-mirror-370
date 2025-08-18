# Pytest Mode

Run evaluations using pytest for CI/CD integration, automated testing, and production deployments.

## Overview

Pytest mode leverages the full pytest ecosystem to run evaluations as tests. This provides:
- Integration with CI/CD pipelines
- Fixtures for resource management
- Parametrization for comparing models
- Parallel execution support
- Rich test reporting

## Basic Usage

```bash
# Run a specific evaluation
pytest eval_model.py::eval_function --experiment my_eval

# Run all evaluations in a file
pytest eval_model.py --experiment my_eval

# Run with custom parameters
pytest eval_model.py --experiment my_eval --samples 100 --concurrent
```


## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--experiment` | Experiment name for session management | `--experiment my_eval` |
| `--samples` | Limit number of samples to process | `--samples 100` |
| `--concurrent` | Enable concurrent execution | `--concurrent` |
| `--storage` | Storage backend configuration | `--storage json://custom/` |
| `-k` | Run evaluations matching keyword patterns | `-k "math or accuracy"` |
| `-m` | Run evaluations matching markers | `-m "not dotevals"` |

## Execution Patterns

### Development Testing

```bash
# Quick test with limited samples (ephemeral experiment)
uv pytest eval_model.py --samples 10

# Test with different concurrency (no experiment persistence)
uv pytest eval_model.py --concurrent
```

!!! info "Ephemeral Experiments"
    When you omit `--experiment`, dotevals creates a temporary experiment that appears in a separate list from your named experiments. This keeps your main experiment history clean while still allowing you to view results from development runs.

### Production Runs

```bash
# Full evaluation with session management
uv pytest eval_model.py --experiment "prod_$(date +%Y%m%d)"

# Resume interrupted evaluation
uv pytest eval_model.py --experiment prod_20241201  # Automatically resumes
```

### Filtering Evaluations

```bash
# Run only evaluations matching a keyword
uv pytest -k "math" --experiment math_only

# Run evaluations with specific names
uv pytest -k "eval_accuracy or eval_speed" --experiment filtered_run

# Run only evaluations (skip regular tests)
uv pytest -m dotevals --experiment eval_only

# Skip all evaluations (run only regular tests)
uv pytest -m "not dotevals"
```

!!! note "Automatic Markers"
    dotevals automatically marks all `@foreach` decorated functions with the `dotevals` marker, making it easy to include or exclude them from test runs.

## Coexistence with Tests

dotevals evaluations can coexist with regular unit tests in the same codebase. This allows you to maintain both evaluation workflows and traditional testing in a unified test suite.

### Mixed Test Suites

You can have both evaluations and tests in the same files or project:

```python
# test_model.py
import pytest
from dotevals import foreach
from dotevals.evaluators import exact_match

# Regular unit test
def test_model_initialization():
    from my_model import MyModel
    model = MyModel()
    assert model.is_ready()

# dotevals evaluation (automatically marked with 'dotevals')
@foreach("question,answer", [("What is 2+2?", "4")])
def eval_model_accuracy(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

### Running Tests Only

To run only regular tests (excluding evaluations):

```bash
# Run all tests except evaluations
uv pytest -m "not dotevals"

# Run specific test files without evaluations
uv pytest test_utils.py -m "not dotevals"

# Run tests matching a pattern, excluding evaluations
uv pytest -k "test_model" -m "not dotevals"
```

### Running Evaluations Only

To run only evaluations (excluding regular tests):

```bash
# Run all evaluations
uv pytest -m dotevals --experiment my_eval

# Run evaluations from specific files
uv pytest eval_model.py -m dotevals --experiment model_eval
```

### Mixed Execution

You can also run both tests and evaluations together:

```bash
# Run everything (tests + evaluations)
uv pytest --experiment mixed_run

# Run tests first, then evaluations if tests pass
uv pytest && uv pytest -m dotevals --experiment post_test_eval
```

!!! tip "Organizing Mixed Suites"
    Consider using separate directories or file naming conventions to organize your test suite:
    ```
    tests/
    ├── unit/           # Regular unit tests
    ├── integration/    # Integration tests
    └── evaluations/    # dotevals evaluations
    ```

### File Discovery

pytest automatically discovers evaluation files and functions:

- **Files**: `eval_*.py` (in addition to standard `test_*.py`)
- **Functions**: `eval_*` (in addition to standard `test_*`)

```python
# This file will be automatically discovered
# eval_math.py
from dotevals import foreach
from dotevals.models import Result
from dotevals.evaluators import exact_match

# Example dataset - replace with your actual data
dataset = [("What is 2+2?", "4"), ("What is 5+3?", "8")]

@foreach("question,answer", dataset)
def eval_arithmetic(question, answer, model):
    # model parameter comes from pytest fixture
    response = model.generate(question)
    return Result(exact_match(response, answer), prompt=question)
```

## Session Management

### Automatic Resumption

Evaluations automatically resume from where they left off:

```bash
# Start evaluation
uv pytest eval_large.py --experiment large_eval

# If interrupted, resume by running same command
uv pytest eval_large.py --experiment large_eval  # Continues from last checkpoint
```

### Incremental Evaluation

Add more samples to existing experiments:

```bash
# Initial run
uv pytest eval_model.py --experiment incremental --samples 500

# Add more samples
uv pytest eval_model.py --experiment incremental --samples 1000

# Process any remaining
uv pytest eval_model.py --experiment incremental
```


## Performance Optimization

### Concurrency Control

**For API-based models:** Configure concurrency strategy in your evaluation setup, not via `--concurrent`. This provides proper rate limiting and shared throttling:

```python
from dotevals import ForEach
from dotevals.evaluators import exact_match
from dotevals.concurrency import RateLimitedConcurrency

# Configure rate-limited concurrency strategy
foreach = ForEach(
    concurrency=RateLimitedConcurrency(
        max_concurrent=5,
        rate_limit=10,  # requests per second
        burst_limit=20
    )
)

@foreach("question,answer", dataset)
async def eval_openai(question, answer, openai_client):
    # Proper rate limiting across all evaluations
    response = await openai_client.chat.completions.create(...)
    return exact_match(response.choices[0].message.content, answer)
```

**For independent processes:** Use `--concurrent` when you can launch separate instances:

```bash
# Each evaluation gets its own model process
uv pytest eval_ollama.py --experiment ollama_eval --concurrent
```

**When to avoid `--concurrent`:**

- API calls (use concurrency strategy instead for proper rate limiting)
- Single shared model instance (most local model setups)
- CPU-bound evaluations where cores are already saturated

### Memory Management

Use streaming datasets for large evaluations:

```python
def streaming_dataset():
    with open("large_dataset.jsonl") as f:
        for line in f:
            data = json.loads(line)
            yield (data["question"], data["answer"])

@foreach("question,answer", streaming_dataset())
def eval_streaming(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

## Viewing Results

After running evaluations, view results using the CLI:

```bash
# View experiment results
dotevals show my_eval

# List all experiments
dotevals list

# View detailed results with full data
dotevals show my_eval --full
```

## See Also

- **[CLI Reference](cli.md)** - Complete command-line options reference
- **[Experiments](experiments.md)** - Session management and state handling
- **[Pytest Integration](pytest.md)** - Deep dive into pytest-specific features
- **[@foreach Decorator](foreach.md)** - Decorator API and configuration options
