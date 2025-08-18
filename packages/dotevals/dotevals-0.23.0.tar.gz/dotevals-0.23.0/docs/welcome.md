# Welcome to dotevals!

**dotevals** is a powerful evaluation framework for Large Language Models that makes testing and measuring LLM performance simple, reproducible, and scalable. Built by [dottxt](https://dottxt.ai), it provides a code-first approach to LLM evaluation.

## New to dotevals?

If you're new to dotevals, check out the **[Core Terminology](concepts/core-terminology.md)** guide to understand the key concepts and terms used throughout the documentation.

## Quick Example

Here's what LLM evaluation looks like with dotevals:

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

# Your test data
dataset = [
    ("What is 2+2?", "4"),
    ("Capital of France?", "Paris"),
    ("What is 10-3?", "7"),
]

# Evaluation function
@foreach("question,answer", dataset)
def eval_accuracy(question, answer, model):
    """Test if the model gets basic facts correct."""
    result = model.generate(question)
    return exact_match(result, answer)

# Run: pytest eval_accuracy.py --experiment baseline
# Result: "Accuracy: 0.67 (2 out of 3 correct)"
```

## Core Concepts

### 1. The `@foreach` Decorator

The heart of dotevals is the `@foreach` decorator (shown in the example above) that transforms a regular function into an evaluation that runs across an entire dataset. The function you decorate computes the *score* for one sample, and `@foreach` automatically applies it to every sample in your dataset before aggregating the results using *metrics*.

This simple decorator handles:

- **Data iteration** - Automatically processes each item in your dataset
- **Error handling** - Gracefully handles failures and continues evaluation
- **Progress tracking** - Shows real-time progress and estimates
- **Experiment management** - Saves state to resume interrupted evaluations

### 2. Evaluators: Scoring Individual Samples

Evaluators determine if a single model output is correct. They take a response and expected answer, then return a score for that one sample:

```python
from dotevals.evaluators import evaluator, exact_match
from dotevals.metrics import accuracy

# Built-in evaluator: checks if two strings match
score = exact_match("Paris", "Paris")  # Returns: True for this one sample

# Custom evaluator: your own scoring logic
@evaluator(metrics=accuracy())
def contains_reasoning(response: str) -> bool:
    """Check if this specific response includes reasoning."""
    keywords = ["because", "therefore", "since", "thus"]
    return any(keyword in response.lower() for keyword in keywords)
```

### 3. Metrics: Aggregating Across All Samples

Metrics take all the individual scores from evaluators and compute overall statistics. While evaluators score one sample, metrics tell you how well your model performed across the entire dataset:

```python
# Evaluator scores each sample: [True, True, False, True, False, True, ...]
# Metric aggregates all scores: "Accuracy: 0.75 (750/1000 correct)"
```

When you run `dotevals show`, you see the aggregated metrics:

```bash
dotevals show my_experiment
# Output: Accuracy: 0.75 (750/1000 correct)
# Output: Mean latency: 1.2s per sample
# Output: Total duration: 20 minutes
```

### 4. Experiment Management

dotevals automatically manages evaluation sessions (experiments) allowing you to:

- **Resume interrupted evaluations** - Power outages, crashes, or manual stops don't lose progress
- **Track multiple experiments** - Organize evaluations by name and compare results

```bash
# Run evaluation
pytest eval_gsm8k.py --experiment my_experiment

# View results
dotevals show my_experiment

# Resume if interrupted (automatically detects incomplete evaluation)
pytest eval_gsm8k.py --experiment my_experiment
```

## Complete Example

Here's a real-world evaluation pipeline:

```python
import pytest
from dotevals import foreach
from dotevals.evaluators import numeric_match
import re

@pytest.fixture
def model():
    from openai import OpenAI
    client = OpenAI()
    return client

math_problems = [
    ("What is 15 + 27?", "42"),
    ("Calculate 100 - 33", "67"),
    ("What is 12 × 5?", "60"),
]

def extract_number(text: str) -> str:
    """Extract number from model response."""
    match = re.search(r'\d+', text)
    return match.group() if match else ""

@foreach("problem,answer", math_problems)
def eval_math(problem, answer, model):
    response = model.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": problem}]
    )
    result = extract_number(response.choices[0].message.content)
    return numeric_match(result, answer)
```

Run it:

```bash
# Start evaluation
pytest eval_math.py --experiment math_test

# View results
dotevals show math_test
# Output: Accuracy: 1.00 (3/3 correct)
```

## Next Steps

### New to dotevals

1. 📖 **[Core Terminology](concepts/core-terminology.md)** - Learn dotevals's concepts
2. 🚀 **[Quickstart Guide](quickstart.md)** - Your first evaluation in 30 seconds
3. 📝 **[Tutorial: Your First Evaluation](tutorials/01-your-first-evaluation.md)** - Step-by-step guide

### Experienced Developer

1. 🚀 **[Quickstart Guide](quickstart.md)** - Jump right in
2. 🔧 **[Using Real Models](tutorials/02-using-real-models.md)** - OpenAI, Anthropic, local models
3. 📊 **[Working with Datasets](tutorials/03-working-with-real-datasets.md)** - HuggingFace and custom data
4. ⚡ **[Async Evaluations](tutorials/05-scale-with-async-evaluation.md)** - Scale with concurrency
