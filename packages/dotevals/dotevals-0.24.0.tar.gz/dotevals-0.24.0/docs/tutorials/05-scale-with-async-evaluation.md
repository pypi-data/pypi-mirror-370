# Tutorial 5: Scale with Async Evaluation

In this tutorial, you'll learn to transform slow synchronous evaluations into fast asynchronous ones.

## What you'll learn

- The difference between sync and async evaluation approaches
- How to convert synchronous evaluations to async
- How to enable concurrent execution with `SlidingWindow`
- When async evaluation provides the biggest benefits
- How to measure and compare performance improvements

## Understanding the Problem: Why Evaluations Are Slow

Before diving into async, let's understand **why** evaluations are slow and **when** async helps.

Most LLM evaluations are **I/O bound** - they spend time waiting for API calls to language models (OpenAI, Anthropic, etc.), to datasets, etc. Ideally our CPU would process other calls while waiting for another one to complete. This is what async execution does.


### CPU vs I/O Bound Tasks

```python
# CPU-bound: Your computer does the work
def cpu_intensive_calculation(n):
    return sum(i**2 for i in range(n))  # Computer calculates this

# I/O-bound: Your computer waits for external systems
def api_call_to_model(prompt):
    response = requests.post("https://api.openai.com/...", ...)  # Wait for network
    return response.json()
```

**Async helps with I/O-bound tasks** (like API calls) but won't speed up CPU-intensive calculations.

## Step 1: Create a Slow Sync Evaluation

Start with a deliberately slow evaluation to see the baseline:

```python title="eval_slow_sync.py"
import time
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

@pytest.fixture
def model():
    """Slow mock model for baseline testing."""
    class SlowModel:
        def classify(self, text):
            time.sleep(1)  # Simulate API latency
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return SlowModel()

def slow_sentiment_model(text):
    """Mock slow model that takes 1 second per call."""
    time.sleep(1)  # Simulate API latency

    # Simple sentiment logic
    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
        return "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

# Test dataset
sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot and awful acting", "negative"),
    ("It was an okay film, nothing special", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing and terrible direction", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad character development", "negative"),
]

@foreach("text,expected", sentiment_data)
def eval_sync_sentiment(text, expected, model):
    """Slow synchronous sentiment evaluation."""
    prediction = model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run and time the sync version:

```bash
time pytest eval_slow_sync.py --experiment sync_baseline
```

You'll see it takes about 8 seconds (8 samples × 1 second each). Note the total time.

This is the problem with real evaluations: testing 1000 samples with a 1-second API latency would take over 16 minutes. That's a coffee break for every evaluation run.

## Understanding Async: The Foundation

Before converting to async, let's understand what `async` and `await` actually do.

### Synchronous Execution (What We Just Ran)
```python
# Synchronous: Each operation blocks until complete
def sync_process():
    result1 = slow_operation_1()  # Wait 1 second
    result2 = slow_operation_2()  # Wait 1 second
    result3 = slow_operation_3()  # Wait 1 second
    # Total: 3 seconds
```

### Asynchronous Execution (What We're Building Toward)
```python
# Asynchronous: Operations can overlap
async def async_process():
    # gather() runs all operations concurrently
    results = await asyncio.gather(
        async_operation_1(),  # Starts immediately
        async_operation_2(),  # Starts immediately
        async_operation_3()   # Starts immediately
    )
    # All three operations run in parallel
    # Total: ~1 second (instead of 3 seconds sequentially)
```

The `asyncio.gather()` function is the key to concurrent execution. It takes multiple async operations and runs them all at the same time, waiting for all to complete before returning their results.


## Step 2: Convert to Async

Now create an async version of the same evaluation:

```python title="eval_async_sentiment.py"
import asyncio
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

@pytest.fixture
def async_model():
    """Async mock model for testing."""
    class AsyncModel:
        async def classify(self, text):
            await asyncio.sleep(1)  # Simulate async API call
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return AsyncModel()

async def async_sentiment_model(text):
    """Mock async model that simulates API latency."""
    await asyncio.sleep(1)  # Simulate async API call

    # Same sentiment logic
    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
        return "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

# Same test dataset
sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot and awful acting", "negative"),
    ("It was an okay film, nothing special", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing and terrible direction", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad character development", "negative"),
]

@foreach("text,expected", sentiment_data)
async def eval_async_sentiment(text, expected, async_model):
    """Async sentiment evaluation."""
    prediction = await async_model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run the async version:

```bash
time pytest eval_async_sentiment.py --experiment async_basic
```

It now takes about 2 seconds instead of 8! This is because **dotevals automatically enables concurrency for async functions** using a default `SlidingWindow` strategy.

For our 1000-sample example? That 16-minute evaluation now takes just 4 minutes with default async. No configuration needed.

### How Doteval Handles Async Functions

When dotevals detects an async function, it automatically:

1. **Enables concurrent execution** with a sensible default concurrency level
2. **Manages the async event loop** for you
3. **Batches evaluations** to run multiple samples simultaneously

```python
# What we wrote (async function)
async def eval_async_sentiment(text, expected, async_model):
    prediction = await async_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)

# How dotevals executes it (concurrent by default for async)
# Automatically uses SlidingWindow concurrency
await asyncio.gather(
    eval_async_sentiment(sample1),
    eval_async_sentiment(sample2),
    eval_async_sentiment(sample3),
    eval_async_sentiment(sample4),
    # ... up to default concurrency limit
)
```

## Step 3: Customize Concurrency

While dotevals provides automatic concurrency for async functions, you can customize the concurrency level for better performance or to respect API rate limits.

Common scenarios where you'd customize:
- **OpenAI Tier 1**: Limited to 500 requests/min → use `max_concurrency=8`
- **Anthropic Claude**: Rate limits vary → start with `max_concurrency=5`
- **Local vLLM server**: Can handle more → try `max_concurrency=50`

```python title="eval_concurrent_sentiment.py"
import asyncio
import pytest
from dotevals import ForEach, Result
from dotevals.evaluators import exact_match
from dotevals.concurrency import SlidingWindow

@pytest.fixture
def async_model():
    """Async mock model for concurrent testing."""
    class AsyncModel:
        async def classify(self, text):
            await asyncio.sleep(1)
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return AsyncModel()

async def async_sentiment_model(text):
    """Mock async model with API latency."""
    await asyncio.sleep(1)

    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
        return "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

# Configure concurrent execution
foreach_concurrent = ForEach(concurrency=SlidingWindow(max_concurrency=8))

sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot and awful acting", "negative"),
    ("It was an okay film, nothing special", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing and terrible direction", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad character development", "negative"),
]

@foreach_concurrent("text,expected", sentiment_data)
async def eval_concurrent_sentiment(text, expected, async_model):
    """Concurrent async sentiment evaluation."""
    prediction = await async_model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run the concurrent version:

```bash
time pytest eval_concurrent_sentiment.py --experiment concurrent_test
```

With explicit `max_concurrency=8`, all 8 samples run simultaneously, completing in about 1 second total!

### Understanding Concurrency Configuration

The `SlidingWindow(max_concurrency=8)` explicitly controls how dotevals executes evaluations:

```python
# Sequential execution (synchronous)
await eval_sample_1()  # 1 second
await eval_sample_2()  # 1 second
await eval_sample_3()  # 1 second
# ... continues for all 8 samples
# Total: 8 seconds

# With SlidingWindow(max_concurrency=8)
await asyncio.gather(
    eval_sample_1(),  # All 8 start together
    eval_sample_2(),
    eval_sample_3(),
    eval_sample_4(),
    eval_sample_5(),
    eval_sample_6(),
    eval_sample_7(),
    eval_sample_8()
)
# Total: ~1 second for all 8 samples
```

## Step 4: Measure Performance Improvements

Compare all three approaches:

```bash
# View timing results
dotevals show sync_baseline
dotevals show async_basic
dotevals show concurrent_test
```

You should see:

- **Sync**: ~8 seconds (baseline, no concurrency)
- **Async with default concurrency**: ~2 seconds (automatic 4x improvement!)
- **Async with custom concurrency=8**: ~1 second (all samples run simultaneously)

The pattern is clear: higher concurrency = faster completion, until you hit rate limits or hardware constraints.

### Choosing the Right Concurrency Level

**Quick guidelines**:
- **Default**: Doteval's automatic concurrency works well for most cases
- **API providers**: OpenAI (10-20), Anthropic (5-10), based on your tier
- **Local models**: Higher values (50-100+) depending on resources
- **Custom tuning**: Start with 10, increase gradually while monitoring for rate limits

!!! warning "Rate Limit Considerations"
    Increasing concurrency speeds up evaluation but also increases the rate of API requests. Always consider your API tier limits when tuning concurrency.

!!! info "Self-Hosted Models: Use Adaptive Strategy"
    For self-hosted models (vLLM, TGI, local GPUs), we recommend using the `Adaptive` concurrency strategy instead of `SlidingWindow`. Adaptive automatically adjusts concurrency based on server response times, finding the optimal throughput without overwhelming your hardware. This prevents OOM errors and maximizes GPU utilization.

    ```python
    from dotevals.concurrency import Adaptive
    foreach_adaptive = ForEach(concurrency=Adaptive())
    ```

    Learn more: [Adaptive Concurrency](../reference/async.md#adaptive)

## What you've learned

You now understand the **async evaluation optimization pattern**:

### 1. Identify I/O Bound Operations

- API calls to language models (OpenAI, Anthropic, etc.)
- Database queries
- File system operations
- Network requests

### 2. Convert Functions to Async
```python
# Before: Synchronous
def eval_sync(prompt, model):
    result = model.generate(prompt)  # Blocks
    return exact_match(result, expected)

# After: Asynchronous (automatic concurrency!)
async def eval_async(prompt, model):
    result = await model.generate(prompt)  # Concurrent by default
    return exact_match(result, expected)
```

### 3. Optionally Tune Concurrency
```python
# Customize for your specific needs
foreach_custom = ForEach(concurrency=SlidingWindow(max_concurrency=10))
```

!!! tip "Key Takeaway"
    Just making your function `async` gives you immediate performance benefits in dotevals. Custom concurrency configuration is for fine-tuning based on your specific requirements.

## The Mental Model

Think of async evaluation like a restaurant:

- **Synchronous**: One waiter takes one order, waits for the kitchen, serves, then takes the next order
- **Asynchronous (default)**: Multiple waiters work simultaneously (dotevals manages the team size)
- **Custom concurrency**: You decide exactly how many waiters to hire

## Next Steps

**[Tutorial 6: Pytest Fixtures and Resource Pooling](06-pytest-fixtures-and-resource-pooling.md)** - Manage expensive resources efficiently with proper fixture scoping.

## Summary

In this tutorial, you learned that:

1. **Sync evaluations are slow** for I/O-bound operations (8 seconds for 8 API calls)
2. **Async functions get automatic concurrency** in dotevals (~2 seconds with default settings)
3. **Custom concurrency gives you control** over performance vs. rate limits
4. **Higher concurrency = faster completion** when within API limits (1 second with concurrency=8)

The key takeaway: Simply converting your evaluation functions to `async` gives you immediate performance benefits in dotevals. Fine-tune concurrency levels only when you need to optimize for specific API limits or performance requirements.
