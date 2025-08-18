# Interactive Mode

The interactive mode allows you to run evaluations programmatically in notebooks, scripts, or REPLs without using pytest.

## Overview

The interactive API provides a simple `run()` function that executes decorated evaluation functions and returns a `Results` object containing all evaluation data.

## Installation

The interactive mode is included in the standard dotevals installation:

```bash
pip install dotevals
```

## Basic Usage

```python
from dotevals import foreach, run
from dotevals.evaluators import exact_match

# Define your dataset
dataset = [
    ("What is 2 + 2?", "4"),
    ("What is 5 × 3?", "15"),
]

# Define your evaluation function with @foreach
@foreach("question,answer", dataset)
def eval_math(question, answer, model):
    result = model.generate(question)
    return exact_match(result, answer)

# Run the evaluation
results = run(eval_math, model=my_model)

# Access the summary
print(results.summary())
```

## Quick Reference

```python
from dotevals import run

# Run evaluation
results = run(eval_function, model=my_model)

# With options
results = run(
    eval_function,
    experiment="gpt4_baseline",
    limit=100,
    storage="sqlite://results.db",
    model=my_model,
    temperature=0.7
)

# Access results
summary = results.summary()
records = results.records
```

For detailed API documentation, see the [Interactive API Reference](../api/interactive.md).

## Working with Decorated Functions

The interactive mode **requires** functions to be decorated with `@foreach`. This ensures consistency between interactive and pytest usage.

### Using the Same Function in Both Modes

```python
# Define once
@foreach("text,label", dataset)
def eval_sentiment(text, label, model):
    prediction = model.predict(text)
    return exact_match(prediction, label)

# Use in pytest
# pytest eval.py::eval_sentiment --experiment baseline

# Use interactively
results = run(eval_sentiment, model=my_model)
```

### Passing Parameters

Any parameters your evaluation function needs should be passed as keyword arguments to `run()`:

```python
@foreach("prompt,expected", dataset)
def eval_with_params(prompt, expected, model, temperature, max_tokens):
    response = model.generate(
        prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return exact_match(response, expected)

# Pass parameters through run()
results = run(
    eval_with_params,
    model=my_model,
    temperature=0.7,
    max_tokens=100
)
```

### Async Support

The interactive mode fully supports both sync and async evaluation functions. Both are handled the same way:

```python
# Sync function
@foreach("question,answer", dataset)
def eval_sync(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)

results = run(eval_sync, model=my_model)
print(results.summary())

# Async function
@foreach("question,answer", dataset)
async def eval_async(question, answer, model):
    response = await model.generate_async(question)
    return exact_match(response, answer)

# Same interface for async functions
results = run(eval_async, model=my_async_model)
print(results.summary())
```

### Working with Parametrized Functions

If your function uses `@pytest.mark.parametrize`, you can still use it interactively by passing the parameter value:

```python
@pytest.mark.parametrize("model_name", ["gpt-3.5", "gpt-4"])
@foreach("question,answer", dataset)
def eval_models(question, answer, model_name):
    model = load_model(model_name)
    result = model.generate(question)
    return exact_match(result, answer)

# In interactive mode, pass the parameter explicitly
results_gpt35 = run(eval_models, model_name="gpt-3.5")
results_gpt4 = run(eval_models, model_name="gpt-4")

# Compare results
print("GPT-3.5:", results_gpt35.summary())
print("GPT-4:", results_gpt4.summary())
```

## Storage Backends

By default, results are stored in `.dotevals` folder using JSON storage. You can specify different storage backends:

```python
# Default JSON storage
results = run(eval_function, model=my_model)

# SQLite storage
results = run(eval_function, storage="sqlite://results.db", model=my_model)

# Custom storage path
results = run(eval_function, storage="json://evaluation_results", model=my_model)
```

## Experiment Names

Experiments are automatically named with timestamps, but you can provide custom names:

```python
# Auto-generated: run_20240115_143022
results = run(eval_function, model=my_model)

# Custom name
results = run(eval_function, experiment="baseline_v2", model=my_model)

# Access the experiment name
print(f"Experiment: {results.experiment}")
```

## Progress Display

The interactive mode automatically shows a progress bar during evaluation:

- For datasets with known size: Shows progress bar with ETA
- For streaming datasets: Shows spinner with completion count

## Example: Comparing Models

```python
from dotevals import foreach, run
from dotevals.evaluators import exact_match

# Load your dataset
dataset = load_dataset("math_problems")

@foreach("problem,solution", dataset)
def eval_math(problem, solution, model):
    answer = model.solve(problem)
    return exact_match(answer, solution)

# Compare different models
models = {
    "gpt-3.5": load_model("gpt-3.5"),
    "gpt-4": load_model("gpt-4"),
    "claude": load_model("claude")
}

results = {}
for name, model in models.items():
    results[name] = run(
        eval_math,
        experiment=f"math_{name}",
        model=model
    )

# Compare results
for name, result in results.items():
    summary = result.summary()
    accuracy = summary['metrics']['exact_match']['accuracy']
    print(f"{name}: {accuracy:.2%}")
```

## Best Practices

1. **Always use `@foreach` decorator**: This ensures your evaluation works in both interactive and pytest modes
2. **Use descriptive experiment names**: Makes it easier to track and compare results
3. **Leverage the same storage**: Use consistent storage backends between interactive and pytest runs
4. **Pass models as parameters**: Keep evaluation functions model-agnostic by passing models as arguments

## See Also

- [foreach Decorator](core.md#foreach) - Learn about the decorator that powers evaluations
- [Storage Backends](storage.md) - Configure different storage options
- [Pytest Integration](../how-to/use-with-pytest.md) - Run the same evaluations with pytest
