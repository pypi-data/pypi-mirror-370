# Tutorial 3: Work with Real Datasets

In this tutorial, you'll learn to create evaluations using data from multiple sources.

## What you'll learn

- How to load custom JSON data into evaluations
- How to integrate HuggingFace datasets with streaming
- How to combine multiple data sources in one evaluation
- How to compare model performance across different data types

## Step 1: Start with Custom Data

Create your own dataset file `custom_sentiment.json`:

```json
{
  "reviews": [
    {"text": "This movie was amazing and thrilling!", "sentiment": "positive"},
    {"text": "Terrible plot and bad acting throughout", "sentiment": "negative"},
    {"text": "Pretty good film with some great moments", "sentiment": "positive"},
    {"text": "Boring and predictable from start to finish", "sentiment": "negative"}
  ]
}
```

Create a basic evaluation:

```python title="eval_multi_source.py"
import json
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

def load_custom_sentiment():
    """Load your custom sentiment data."""
    with open("custom_sentiment.json") as f:
        data = json.load(f)

    for review in data["reviews"]:
        yield (review["text"], review["sentiment"])

@foreach("text,expected", load_custom_sentiment())
def eval_sentiment_custom(text, expected):
    """Evaluate sentiment on your custom data."""
    # Simple mock sentiment classifier
    if any(word in text.lower() for word in ["amazing", "great", "good"]):
        prediction = "positive"
    elif any(word in text.lower() for word in ["terrible", "bad", "boring"]):
        prediction = "negative"
    else:
        prediction = "neutral"

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Test it works:

```bash
pytest eval_multi_source.py::eval_sentiment_custom --experiment custom_test
```

## Step 2: Add HuggingFace Dataset

Now add a real HuggingFace dataset:

```python
from datasets import load_dataset

def load_imdb_sample():
    """Load sample from IMDB dataset."""
    dataset = load_dataset("imdb", split="test", streaming=True)

    for item in dataset:
        label = "positive" if item["label"] == 1 else "negative"
        yield (item["text"], label)

@foreach("text,expected", load_imdb_sample())
def eval_sentiment_imdb(text, expected):
    """Evaluate sentiment on IMDB data."""
    # Same mock classifier
    if any(word in text.lower() for word in ["amazing", "great", "excellent", "wonderful"]):
        prediction = "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "horrible", "worst"]):
        prediction = "negative"
    else:
        prediction = "positive"  # Default positive bias

    return Result(
        exact_match(prediction, expected),
        prompt=text[:100] + "..."  # Truncate long movie reviews
    )
```

Test the HuggingFace data:

```bash
pytest eval_multi_source.py::eval_sentiment_imdb --experiment imdb_test
```

## Step 3: Combine All Sources

Create one evaluation that uses all your data sources:

```python
def combined_sentiment_data():
    """Combine all sentiment data sources."""
    # Custom data
    for text, sentiment in load_custom_sentiment():
        yield (text, sentiment, "custom")

    # IMDB data
    for text, sentiment in load_imdb_sample():
        yield (text, sentiment, "imdb")

@foreach("text,expected,source", combined_sentiment_data())
def eval_sentiment_combined(text, expected, source):
    """Evaluate sentiment across all data sources."""
    # Your sentiment model here
    positive_words = ["amazing", "great", "excellent", "wonderful", "fantastic"]
    negative_words = ["terrible", "awful", "horrible", "worst", "bad"]

    text_lower = text.lower()
    if any(word in text_lower for word in positive_words):
        prediction = "positive"
    elif any(word in text_lower for word in negative_words):
        prediction = "negative"
    else:
        prediction = "positive"  # Default

    return Result(
        exact_match(prediction, expected),
        prompt=f"[{source}] {text[:60]}..."
    )
```

Run the combined evaluation:

```bash
pytest eval_multi_source.py::eval_sentiment_combined --experiment combined_sentiment
```

## Step 4: Compare Results

View results from all your experiments:

```bash
dotevals list
```

Compare how your model performs on different data sources:

```bash
dotevals show custom_test
dotevals show imdb_test
dotevals show combined_sentiment
```

You'll see how performance varies across different data sources, helping you understand your model's strengths and weaknesses.

## What you've learned

You now understand:

1. **Loading custom data** - Using generator functions to load JSON datasets
2. **HuggingFace integration** - Streaming datasets efficiently
3. **Multi-source evaluation** - Combining different data sources
4. **Performance comparison** - Understanding how models perform on different data types

## Next Steps

**[Tutorial 4: Building Custom Evaluators](04-building-custom-evaluators.md)** - Create sophisticated evaluation logic beyond exact matching.
