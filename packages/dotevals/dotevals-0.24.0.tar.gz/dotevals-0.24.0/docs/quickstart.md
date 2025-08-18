# Quickstart

Get your first evaluation running in under 5 minutes.

## Prerequisites

- Python 3.10+
- dotevals installed: `pip install dotevals`

## 30-Second Example

Create a file called `eval_simple.py`:

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

# Simple test data
math_problems = [
    ("What is 2+2?", "4"),
    ("What is 5+3?", "8"),
    ("What is 10-7?", "3"),
]

@foreach("question,answer", math_problems)
def eval_math(question, answer):
    """Simple math evaluation - replace with your model."""
    # For demo: just return the expected answer
    # Replace this with your actual model call
    model_response = answer  # Simulated perfect model

    return exact_match(model_response, answer)
```

!!! tip "Return Patterns"
    Evaluation functions can return results in two ways:

    **Simple pattern** (recommended for single scores):
    ```python
    return exact_match(model_response, answer)
    ```

    **Explicit pattern** (for multiple scores or additional metadata):
    ```python
    from dotevals.models import Result
    return Result(
        exact_match(model_response, answer),
        prompt=question,
        model_response=model_response
    )
    ```

## Run Your Evaluation

=== "Interactive (Notebooks/Scripts)"

    ```python
    from dotevals import run

    # Run the evaluation
    results = run(eval_math)

    # View results immediately
    print(results.summary())
    # {'total': 3, 'errors': 0, 'metrics': {'exact_match': {'accuracy': 1.0}}}
    ```

=== "pytest (CI/CD)"

    ```bash
    # Run the evaluation
    uv pytest eval_simple.py::eval_math --experiment my_first_eval

    # View results
    dotevals show my_first_eval
    ```

You should see output showing 3/3 correct answers.

## With a Real Model

Replace the simulation with an actual model call:

```python
import pytest
from openai import OpenAI

@pytest.fixture
def openai_client():
    """OpenAI client fixture (requires OPENAI_API_KEY)."""
    return OpenAI()

@foreach("question,answer", math_problems)
def eval_math(question, answer, openai_client):
    """Math evaluation with real model."""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )

    model_response = response.choices[0].message.content.strip()
    return exact_match(model_response, answer)
```

=== "Interactive"

    ```python
    from dotevals import run

    # Call the fixture as a regular function
    client = openai_client()

    # Run evaluation
    results = run(eval_math, openai_client=client)
    print(results.summary())
    ```

=== "pytest"

    ```bash
    # pytest automatically handles the fixture
    pytest eval_simple.py::eval_math --experiment openai_test
    ```

!!! info "Why use a fixture?"
    The `openai_client` fixture creates the OpenAI client **once** for the entire evaluation. Without a fixture, if you instantiated the client inside the evaluation function, it would create a new client for **every sample** in your dataset (potentially hundreds or thousands of times!). Fixtures ensure efficient resource management and can be called as regular functions in interactive mode.

## Next Steps

Ready for more? **[Tutorial 1: Your First Evaluation](tutorials/01-your-first-evaluation.md)** walks through a complete evaluation with real datasets.

## See Also

- **[Tutorial 2: Using Real Models](tutorials/02-using-real-models.md)** - Connect to OpenAI and other APIs
- **[Reference: CLI](reference/cli.md)** - Complete command-line reference
