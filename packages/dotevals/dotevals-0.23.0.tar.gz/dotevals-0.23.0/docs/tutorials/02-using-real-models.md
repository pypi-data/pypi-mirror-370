# Tutorial 2: Connect to Real Models

In this tutorial, you'll connect your evaluations to actual language models instead of mock functions. By the end, you'll understand the basic patterns for integrating with APIs and local models.

## What you'll learn

- How to connect evaluations to OpenAI GPT models
- How to integrate local models via Ollama
- Basic patterns for working with real model APIs
- How to compare API vs local model results

## Step 1: Set Up OpenAI Integration

First, install the OpenAI client and set up your API key:

```bash
pip install openai outlines
export OPENAI_API_KEY="your-api-key-here"
```

Create your first real model evaluation:

```python title="eval_openai_sentiment.py"
import os
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match
from openai import OpenAI
import outlines
from outlines.inputs import Chat

@pytest.fixture
def openai_model():
    """OpenAI client for model calls."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return outlines.from_openai(client, "gpt-3.5-turbo")

# Test dataset
sentiment_data = [
    ("I absolutely love this product!", "positive"),
    ("This is terrible and disappointing", "negative"),
    ("It's an okay product, nothing special", "neutral"),
    ("Amazing quality and great value!", "positive"),
    ("Completely useless and broken", "negative"),
]

@foreach("text,expected", sentiment_data)
def eval_openai_sentiment(text, expected, openai_model):
    """Evaluate sentiment classification with OpenAI."""
    prediction = openai_model(
        Chat([
            {"role": "system", "content": "Classify the sentiment as: positive, negative, or neutral. Respond with only one word."},
            {"role": "user", "content": text}
        ]),
        max_tokens=10,
        temperature=0  # Deterministic responses
    )

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

!!! info "Understanding Fixtures"
    The `@pytest.fixture` decorator creates a reusable component that provides resources to your evaluation functions. In this example:

    - `openai_model()` is a fixture that sets up the OpenAI client once
    - When `eval_openai_sentiment` includes `openai_model` as a parameter, pytest automatically calls the fixture and passes its return value
    - This pattern keeps your code organized and avoids repeating setup code

    Fixtures are especially useful for:
    - Setting up model clients that can be reused across multiple evaluations
    - Managing resources that need cleanup after tests
    - Sharing expensive operations (like model loading) between evaluations

    Learn more about fixtures in the [pytest documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html).

Run your first real model evaluation:

```bash
pytest eval_openai_sentiment.py --experiment openai_sentiment_test
```


## Step 2: Try Local Models

Use Ollama for local models that don't require API costs:

```bash
# Install Ollama Python SDK
pip install ollama

# Install and start Ollama (download from https://ollama.ai/)
# Then pull a model
ollama pull llama3.2  # or another model like llama2, mistral, etc.
ollama serve
```

```python title="eval_local_models.py"
import pytest
from ollama import Client
from dotevals import foreach, Result
from dotevals.evaluators import exact_match
import outlines

@pytest.fixture
def ollama_model():
    """Ollama client for local models."""
    client = Client(host="http://localhost:11434")
    return outlines.from_ollama(client, "llama3.2")

# Test dataset
sentiment_data = [
    ("I absolutely love this product!", "positive"),
    ("This is terrible and disappointing", "negative"),
    ("It's an okay product, nothing special", "neutral"),
    ("Amazing quality and great value!", "positive"),
    ("Completely useless and broken", "negative"),
]

@foreach("text,expected", sentiment_data)
def eval_ollama_sentiment(text, expected, ollama_model):
    """Evaluate sentiment with local Ollama model."""
    prompt = f"""Classify the sentiment of this text as either "positive", "negative", or "neutral".
Respond with only one word.

Text: {text}

Sentiment:"""

    response = ollama_model(prompt)

    # Extract sentiment from response
    if "positive" in response:
        prediction = "positive"
    elif "negative" in response:
        prediction = "negative"
    else:
        prediction = "neutral"

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

!!! tip "Fixtures work the same way for any model"
    Just like with OpenAI, the `ollama_model` fixture sets up the model client once and provides it to your evaluation function. The beauty of fixtures is that they work identically regardless of the model provider - whether it's an API service or a local model.

Run the local model evaluation:

```bash
pytest eval_local_models.py --experiment ollama_test
```

## Step 3: Compare Different Models

Create a side-by-side comparison:

```python title="eval_model_comparison.py"
import os
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match
from openai import OpenAI
from ollama import Client
import outlines
from outlines.inputs import Chat

@pytest.fixture
def openai_model():
    """OpenAI model via outlines."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return outlines.from_openai(client, "gpt-3.5-turbo")

@pytest.fixture
def ollama_model():
    """Ollama model via outlines."""
    client = Client(host="http://localhost:11434")
    return outlines.from_ollama(client, "llama3.2")

# Test dataset
sentiment_data = [
    ("I absolutely love this product!", "positive"),
    ("This is terrible and disappointing", "negative"),
    ("It's an okay product, nothing special", "neutral"),
    ("Amazing quality and great value!", "positive"),
    ("Completely useless and broken", "negative"),
]

# Compare both models on the same data
@foreach("text,expected", sentiment_data)
def eval_model_comparison(text, expected, openai_model, ollama_model):
    """Compare OpenAI and local model performance."""

    # Get OpenAI prediction
    openai_prediction = openai_model(
        Chat([
            {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
            {"role": "user", "content": text}
        ]),
        max_tokens=5,
        temperature=0
    ).strip().lower()

    # Get Ollama prediction
    ollama_response = ollama_model(
        f"Classify sentiment as positive, negative, or neutral: {text}\nSentiment:",
    ).strip().lower()

    # Extract sentiment from Ollama response
    if "positive" in ollama_response:
        ollama_prediction = "positive"
    elif "negative" in ollama_response:
        ollama_prediction = "negative"
    else:
        ollama_prediction = "neutral"

    return Result(
        exact_match(openai_prediction, expected, name="openai_accuracy"),
        exact_match(ollama_prediction, expected, name="ollama_accuracy"),
        prompt=text,
        model_response=f"OpenAI: {openai_prediction}, Ollama: {ollama_prediction}"
    )
```

!!! note "Using Multiple Fixtures"
    Notice how `eval_model_comparison` uses both `openai_model` and `ollama_model` fixtures? You can use as many fixtures as you need in your evaluation functions - pytest will automatically provide all of them. This makes it easy to:

    - Compare multiple models side-by-side
    - Mix different resources (models, databases, configuration)
    - Keep your evaluation logic clean and focused

Run the comparison:

```bash
pytest eval_model_comparison.py --experiment model_comparison
```

View the results:

```bash
dotevals show model_comparison
```

## What you've learned

You now understand:

1. **Basic API integration** - How to connect evaluations to OpenAI models
2. **Local model setup** - Using Ollama for cost-free evaluation
3. **Simple error handling** - Basic patterns for handling API failures
4. **Model comparison** - Running the same evaluation on different models
5. **API vs local tradeoffs** - Understanding the differences between approaches

## Key takeaways

- Set `temperature=0` for consistent evaluation results
- Always include basic error handling for API calls
- Local models are free but may need more setup
- Comparing models helps you understand their strengths
- Start simple - you can always add more sophistication later

## Next Steps

**[Tutorial 3: Working with Real Datasets](03-working-with-real-datasets.md)** - Load and work with real evaluation datasets from multiple sources.
