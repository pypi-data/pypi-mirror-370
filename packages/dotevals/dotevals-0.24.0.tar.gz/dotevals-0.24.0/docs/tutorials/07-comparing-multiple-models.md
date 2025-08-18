# Tutorial 7: Compare Multiple Models

In this tutorial, you'll learn to evaluate multiple models on the same dataset using pytest parametrization.

## What you'll learn

- How to use `@pytest.mark.parametrize` with `indirect=True` for model comparison
- How to create pooled model instances for efficient testing
- How to generate test parameters dynamically
- How to evaluate models across different task categories
- How to analyze and compare results across models

## Step 1: Understanding pytest Parametrization Basics

Before jumping into model comparison, let's understand how pytest parametrization works with fixtures.

### Simple Parametrization

First, let's see basic parametrization without models:

```python
import pytest

# Simple values parametrization
@pytest.mark.parametrize("number", [1, 2, 3])
def test_simple_numbers(number):
    """Basic parametrization - one test per parameter value."""
    assert number > 0
    print(f"Testing number: {number}")

# Multiple parameters
@pytest.mark.parametrize("text,expected", [
    ("hello", 5),
    ("world", 5),
    ("pytest", 6)
])
def test_string_lengths(text, expected):
    """Test with multiple parameter values."""
    assert len(text) == expected
```

### The `indirect=True` Pattern

When you use `indirect=True`, pytest passes the parameter values to a fixture instead of directly to the test:

```python
@pytest.fixture
def processed_data(request):
    """Fixture that processes the parameter value."""
    raw_value = request.param  # Get the parameter passed from parametrize

    # Process the raw value
    if raw_value == "simple":
        return {"type": "basic", "complexity": 1}
    elif raw_value == "advanced":
        return {"type": "complex", "complexity": 10}
    else:
        return {"type": "unknown", "complexity": 5}

@pytest.mark.parametrize("processed_data", ["simple", "advanced", "unknown"], indirect=True)
def test_with_indirect(processed_data):
    """Test using indirect parametrization."""
    assert "type" in processed_data
    assert processed_data["complexity"] > 0
    print(f"Processing: {processed_data}")
```

The key insight: `indirect=True` lets you transform parameter values through fixtures before they reach your test.

## What Can You Parametrize?

Parametrization is powerful for testing different configurations systematically. Here are common use cases in evaluations:

- Compare different models, versions, or configurations:
- Test how evaluation parameters such as temperatture affect the evaluation results.
- Test different prompt strategies and templates.

Example of parametrizing prompts and evaluation settings:

```python
@pytest.mark.parametrize("temperature", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("prompt_style", ["simple", "detailed"])
@foreach("text,expected", sentiment_data)
def eval_temperature_and_prompts(text, expected, temperature, prompt_style):
    """Test how temperature and prompt style affect results."""

    if prompt_style == "simple":
        system_prompt = "Classify sentiment: positive, negative, neutral"
    else:
        system_prompt = """You are an expert sentiment analyzer.
        Classify the sentiment as positive, negative, or neutral based on emotional tone."""

    # Use the parameters in your model call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=temperature,
        max_tokens=5
    )

    prediction = response.choices[0].message.content.strip().lower()
    return Result(
        exact_match(prediction, expected),
        metadata={"temperature": temperature, "prompt_style": prompt_style}
    )
```

## Step 2: Basic Model Parametrization

Now let's apply this pattern to model comparison. First, let's define the models we will be using:

```python title="eval_model_comparison.py"
import os
from openai import OpenAI

# Model classes
class GPT35Model:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.name = "gpt-3.5-turbo"

    def classify_sentiment(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
                    {"role": "user", "content": text}
                ],
                max_tokens=5,
                temperature=0
            )
            return response.choices[0].message.content.strip().lower()
        except:
            return "neutral"

class GPT4Mini:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.name = "gpt-4o-mini"

    def classify_sentiment(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
                    {"role": "user", "content": text}
                ],
                max_tokens=5,
                temperature=0
            )
            return response.choices[0].message.content.strip().lower()
        except:
            return "neutral"
```

Now let's use pytest parametrization to compare these models:

```python
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

# Define model configurations
model_configs = [
    "gpt-3.5-turbo",
    "gpt-4o-mini"
]

@pytest.fixture
def model(request):
    """Model fixture that creates different models based on parameter."""
    model_name = request.param

    if model_name == "gpt-3.5-turbo":
        return GPT35Model()
    elif model_name == "gpt-4o-mini":
        return GPT4Mini()
    else:
        raise ValueError(f"Unknown model: {model_name}")

# Test dataset
sentiment_data = [
    ("I love this product!", "positive"),
    ("This is terrible quality", "negative"),
    ("It's an okay product", "neutral"),
    ("Amazing experience!", "positive"),
    ("Awful customer service", "negative"),
]

@pytest.mark.parametrize("model", model_configs, indirect=True)
@foreach("text,expected", sentiment_data)
def eval_sentiment_comparison(text, expected, model):
    """Compare sentiment classification across different models."""
    prediction = model.classify_sentiment(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text,
        metadata={"model_name": model.name}
    )
```

Run the comparison:

```bash
pytest eval_model_comparison.py --experiment model_comparison_basic
```

## What you've learned

You now understand:

1. **Pytest parametrization basics** - How `@pytest.mark.parametrize` works with `indirect=True`
2. **Model parametrization** - Creating different OpenAI models based on parameters
3. **Fixture-based model creation** - Using fixtures to instantiate different model configurations
4. **Metadata tracking** - Adding model names to evaluation results for comparison


## Next Steps

**[Tutorial 8: Build Production Evaluation Pipeline](08-build-production-evaluation-pipeline.md)** - Create a complete evaluation pipeline for production use.
