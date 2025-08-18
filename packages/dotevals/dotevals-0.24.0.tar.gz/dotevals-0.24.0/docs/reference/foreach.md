# The @foreach Decorator

The `@foreach` decorator is the heart of dotevals. It transforms a regular Python function into an evaluation that automatically runs across an entire dataset, handling data iteration, error management, progress tracking, and session management.

## Basic Usage

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

@foreach("question,answer", dataset)
def eval_model(question, answer, model):
    """Evaluate model on question-answer pairs."""
    response = model.generate(question)
    return exact_match(response, answer)
```

## Column Specification

The `column_spec` parameter defines how dataset items map to function arguments:

### Simple Mapping

```python
from dotevals.evaluators import exact_match

# Dataset: [("What is 2+2?", "4"), ("What is 3+3?", "6")]
@foreach("question,answer", math_dataset)
def eval_math(question, answer, model):
    # question gets "What is 2+2?"
    # answer gets "4"
    result = model.solve(question)
    return exact_match(result, answer)
```

### Complex Data Structures

```python
# Dataset with nested data
dataset = [
    {"text": "Hello world", "metadata": {"difficulty": "easy"}, "expected": "greeting"},
    {"text": "Complex text", "metadata": {"difficulty": "hard"}, "expected": "complex"}
]

@foreach("text,expected", dataset)
def eval_classification(text, expected, model):
    # Only extracts 'text' and 'expected' fields
    prediction = model.classify(text)
    return exact_match(prediction, expected)
```

### Multiple Column Formats

```python
from dotevals.evaluators import exact_match

# Single column
@foreach("text,expected", text_dataset)
def eval_single(text, expected, model):
    result = model.process(text)
    return exact_match(result, expected)

# Many columns
@foreach("input,expected,context,difficulty", complex_dataset)
def eval_complex(input, expected, context, difficulty, model):
    response = model.generate(input, context=context)
    return context_aware_match(response, expected, difficulty)
```

## Return Values

Evaluation functions can return either a score directly or a `Result` object for additional metadata:

### Direct Score Return

```python
from dotevals.evaluators import exact_match

@foreach("prompt,expected", dataset)
def eval_simple(prompt, expected, model):
    response = model.generate(prompt)
    return exact_match(response, expected)  # Returns score directly
```

### Result Object Return

For additional metadata (prompts, errors, custom data), use the `Result` class:

```python
from dotevals.models import Result
from dotevals.evaluators import exact_match

# Result signature: Result(scores, prompt=None, error=None, **metadata)
@foreach("prompt,expected", dataset)
def eval_with_metadata(prompt, expected, model):
    response = model.generate(prompt)
    score = exact_match(response, expected)
    return Result(score, prompt=prompt, model_response=response)
```

### Multiple Return Values

```python
from dotevals.models import Result

@foreach("text,expected_sentiment,expected_topic", dataset)
def eval_multi_task(text, expected_sentiment, expected_topic, model):
    result = model.analyze(text)

    sentiment_score = exact_match(result.sentiment, expected_sentiment)
    topic_score = exact_match(result.topic, expected_topic)

    return Result([sentiment_score, topic_score], prompt=text)
```

## Dataset Formats

The `@foreach` decorator works with various dataset formats:

### Python Lists

```python
from dotevals.evaluators import exact_match

dataset = [
    ("What is the capital of France?", "Paris"),
    ("What is 2+2?", "4"),
    ("Name a color", "red")
]

@foreach("question,answer", dataset)
def eval_qa(question, answer, model):
    return exact_match(model.answer(question), answer)
```

### Generators

```python
import json
from dotevals.evaluators import exact_match

def load_data():
    """Generator that yields data items."""
    with open("dataset.jsonl") as f:
        for line in f:
            item = json.loads(line)
            yield (item["question"], item["answer"])

@foreach("question,answer", load_data())
def eval_from_file(question, answer, model):
    return exact_match(model.answer(question), answer)
```

### Hugging Face Datasets

```python
from datasets import load_dataset
from dotevals.evaluators import exact_match

def gsm8k_data():
    """Load and format GSM8K dataset."""
    dataset = load_dataset("gsm8k", "main", split="test", streaming=True)
    for item in dataset:
        question = item["question"]
        # Extract answer from solution text
        answer = extract_answer(item["answer"])
        yield (question, answer)

@foreach("question,answer", gsm8k_data())
def eval_gsm8k(question, answer, model):
    response = model.solve(question)
    return exact_match(response, answer)
```

### Custom Iterators

```python
import json
from dotevals.evaluators import exact_match

class CustomDataset:
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(self.data_path) as f:
            for line in f:
                data = json.loads(line)
                yield (data["input"], data["output"])

dataset = CustomDataset("my_data.jsonl")

@foreach("input,output", dataset)
def eval_custom(input, output, model):
    result = model.process(input)
    return exact_match(result, output)
```

## Registered Dataset Syntax

For plugin datasets, you can use them directly by name after installation:

```python
from dotevals import foreach
from dotevals.evaluators import exact_match
from dotevals.models import Result

# First install: pip install dotevals-datasets-common
from dotevals.datasets import gsm8k

@foreach("question,answer", gsm8k())
def eval_math_reasoning(question, answer, model):
    """Evaluate on GSM8K dataset."""
    response = model.solve(question)
    return exact_match(response, answer)
```

This provides:

- Automatic dataset loading and preprocessing
- Progress bars with dataset names and sizes
- Consistent column naming across datasets

### Available Dataset Plugins

No datasets are included by default. Install dataset plugins to use registered datasets:

```bash
# Install common evaluation datasets
pip install dotevals-datasets-common
```

Available datasets (after installing plugins):

- `gsm8k`: Grade school math problems
- `mmlu`: Massive Multitask Language Understanding
- `arc`: AI2 Reasoning Challenge
- And more...

See the [datasets reference](datasets.md) for complete details on available dataset plugins.

## Session Management

The decorator automatically integrates with dotevals's session management, providing automatic resume capabilities for interrupted evaluations:

```python
from dotevals.evaluators import exact_match

@foreach("question,answer", large_dataset)
def eval_large_dataset(question, answer, model):
    """Evaluation with automatic session management."""
    response = model.generate(question)
    return exact_match(response, answer)
```

## Advanced Configuration

### Function Signature

The `@foreach` decorator can be used in two ways:

#### 1. Direct Usage (Default)

```python
def foreach(column_spec: str, dataset: Iterator) -> Callable
```

**Parameters:**

- **column_spec** (`str`): Comma-separated list of column names that map to dataset fields
- **dataset** (`Iterator`): An iterator of tuples/lists representing dataset rows

**Returns:** A decorated function that can be used as a regular function or integrated with testing frameworks

#### 2. Configured Instance

```python
from dotevals import ForEach

foreach = ForEach(
    retries: Optional[AsyncRetrying] = None,
    concurrency: Optional[object] = None,
    storage: Optional[Storage] = None
)
```

**Parameters:**

- **retries** (`Optional[AsyncRetrying]`): Custom retry strategy using tenacity
- **concurrency** (`Optional[object]`): Custom concurrency strategy (AsyncConcurrencyStrategy or SyncConcurrencyStrategy)
- **storage** (`Optional[Storage]`): Custom storage backend

**Returns:** A configured ForEach instance with custom behavior

### Custom Retry Configuration

Configure retry behavior for handling transient failures:

```python
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotevals import ForEach
from dotevals.models import Result
import aiohttp

# Custom retry strategy for API calls
api_retries = AsyncRetrying(
    retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)

# Create ForEach instance with custom retries
foreach = ForEach(retries=api_retries)

@foreach("prompt,expected", dataset)
async def eval_api_model(prompt, expected, api_model):
    """Evaluation with automatic retries on API errors."""
    response = await api_model.generate(prompt)
    return exact_match(response, expected)
```

### Custom Concurrency Strategies

Configure concurrency behavior for the decorator:

```python
from dotevals import ForEach
from dotevals.concurrency import SlidingWindow, Batch, Sequential, Adaptive

# Adaptive concurrency (default for async)
adaptive = Adaptive()
foreach_async = ForEach(concurrency=adaptive)

# Sliding window concurrency
sliding_window = SlidingWindow(max_concurrency=20)
foreach_sliding = ForEach(concurrency=sliding_window)

# Batch processing (for sync functions)
batch_strategy = Batch(batch_size=50)
foreach_batch = ForEach(concurrency=batch_strategy)

# Sequential processing (default for sync)
sequential = Sequential()
foreach_seq = ForEach(concurrency=sequential)
```

### Complete Configuration Example

```python
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed
from dotevals import ForEach
from dotevals.concurrency import SlidingWindow
from dotevals.evaluators import exact_match

foreach = ForEach(
    retries=AsyncRetrying(stop=stop_after_attempt(3), wait=wait_fixed(2)),
    concurrency=SlidingWindow(max_concurrency=10)
)

@foreach("prompt,expected", test_prompts)
async def eval_configured(prompt, expected, api_client):
    response = await api_client.complete(prompt)
    return exact_match(response, expected)
```

## See Also

### Core Concepts
- **[Evaluators](evaluators.md)** - Learn how to create and use evaluators within `@foreach` decorated functions
- **[Experiments](experiments.md)** - Understand how `@foreach` automatically creates and manages evaluation experiments
- **[Data Handling](datasets.md)** - Explore dataset formats, column specifications, and registered datasets compatible with `@foreach`

### Integration Guides
- **[Running Evaluations](running-evaluations.md)** - Complete guide on executing `@foreach` functions, including pytest integration, CLI options, and programmatic execution
- **[Async Evaluations](async.md)** - Scale your evaluations with async `@foreach` functions and concurrency control

### Advanced Usage
- **[Metrics](metrics.md)** - Configure custom metrics that aggregate results from `@foreach` evaluations
- **[Storage Backends](storage.md)** - Customize where `@foreach` sessions store evaluation results

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with basic `@foreach` usage
- **[Scale with Async Evaluation](../tutorials/05-scale-with-async-evaluation.md)** - Transform sync evaluations to async for better performance
- **[Pytest Fixtures and Resource Pooling](../tutorials/06-pytest-fixtures-and-resource-pooling.md)** - Use pytest fixtures with `@foreach` functions
