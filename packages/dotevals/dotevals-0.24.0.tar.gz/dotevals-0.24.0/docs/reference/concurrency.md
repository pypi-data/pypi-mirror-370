# Concurrency Strategies

Control how evaluations run concurrently to optimize performance and manage resources.

## Default Behavior (No Configuration Needed)

**For most users, async just works automatically:**

```python
# Sync function - runs sequentially (default)
@foreach("question,answer", dataset)
def eval_math(question, answer, model):
    return exact_match(model.generate(question), answer)

# Async function - runs concurrently with sensible defaults (default)
@foreach("question,answer", dataset)
async def eval_async_math(question, answer, async_model):
    return exact_match(await async_model.generate(question), answer)
```

**Automatic behavior:**

- **Sync functions**: Sequential execution (one at a time)
- **Async functions**: Concurrent execution with adaptive concurrency
- **Concurrency level**: Automatically determined based on system resources
- **Rate limiting**: Built-in protection against overwhelming APIs

**When to configure:** Only when you need specific concurrency limits or have rate limiting requirements.

## Basic Async Evaluation

Define async evaluation functions using `async`/`await` syntax:

```python
import dotevals
from dotevals.evaluators import exact_match

dataset = [("What is 2+2?", "4"), ("What is 3+3?", "6")]

@dotevals.foreach("question,answer", dataset)
async def eval_async_math(question, answer, async_model):
    result = await async_model.generate(question)
    return exact_match(result, answer)
```

## Concurrency Control

### Simple Concurrency Control

**Most common pattern - just enable concurrent execution:**

```bash
# Enable concurrency (uses automatic limits)
pytest eval_async.py --concurrent
```

**For specific limits, configure in code:**

```python
from dotevals import ForEach

# Simple: limit concurrent requests to 10
foreach = ForEach(max_concurrency=10)

@foreach("question,answer", dataset)
async def eval_limited(question, answer, model):
    return exact_match(await model.generate(question), answer)
```

### Advanced Concurrency Strategies

For complex scenarios, use specialized strategies:

```python
from dotevals import ForEach
from dotevals.concurrency import SlidingWindow, Adaptive

# Sliding window concurrency
foreach_sliding = ForEach(concurrency=SlidingWindow(max_concurrency=20))

@foreach_sliding("question,answer", dataset)
async def eval_sliding_window(question, answer, model):
    result = await model.generate(question)
    return exact_match(result, answer)

# Adaptive concurrency (default for async)
foreach_adaptive = ForEach(concurrency=Adaptive())

@foreach_adaptive("question,answer", dataset)
async def eval_adaptive(question, answer, model):
    result = await model.generate(question)
    return exact_match(result, answer)
```

#### SlidingWindow Parameters

```python
SlidingWindow(max_concurrency: int = 10)
```

**Parameters:**

- `max_concurrency` (int, default=10): Maximum number of concurrent tasks. Fixed concurrency level that doesn't adapt to system performance.

#### Adaptive Parameters

```python
Adaptive(
    initial_concurrency: int = 5,
    min_concurrency: int = 1,
    max_concurrency: int = 100,
    adaptation_interval: float = 2.0,
    throughput_window: int = 20,
    increase_threshold: float = 0.98,
    decrease_threshold: float = 0.90,
    stability_window: int = 3,
    error_backoff_factor: float = 0.7,
)
```

**Parameters:**

- `initial_concurrency` (int, default=5): Starting concurrency level when evaluation begins
- `min_concurrency` (int, default=1): Minimum allowed concurrency level
- `max_concurrency` (int, default=100): Maximum allowed concurrency level
- `adaptation_interval` (float, default=2.0): Seconds between adaptation decisions
- `throughput_window` (int, default=20): Number of completions to track for throughput calculations
- `increase_threshold` (float, default=0.98): Increase concurrency if current/previous throughput ratio > this value
- `decrease_threshold` (float, default=0.90): Decrease concurrency if current/previous throughput ratio < this value
- `stability_window` (int, default=3): Number of measurements before changing direction
- `error_backoff_factor` (float, default=0.7): Multiply concurrency by this factor when errors occur

### Default Behavior

Async functions use `Adaptive` strategy by default, which automatically adjusts concurrency based on system performance.

## Async Model Integration

### OpenAI Async Client

```python
import openai

client = openai.AsyncOpenAI()

@dotevals.foreach("question,answer", dataset)
async def eval_openai(question, answer):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    result = response.choices[0].message.content
    return exact_match(result, answer)
```

### Anthropic Async Client

```python
import anthropic

client = anthropic.AsyncAnthropic()

@dotevals.foreach("question,answer", dataset)
async def eval_anthropic(question, answer):
    response = await client.messages.create(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": question}]
    )
    result = response.content[0].text
    return exact_match(result, answer)
```

## Retry Configuration

### Default Retry Behavior

Async evaluations automatically retry on connection errors:

- 3 retry attempts
- Exponential backoff with jitter
- Retries connection errors, timeouts, and network errors

### Custom Retry Strategy

```python
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed, retry_if_exception_type
from dotevals import ForEach
import aiohttp

api_retries = AsyncRetrying(
    retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_fixed(2)
)

foreach = ForEach(retries=api_retries)

@foreach("question,answer", dataset)
async def eval_with_retries(question, answer, api_client):
    response = await api_client.generate(question)
    return exact_match(response, answer)
```

#### ForEach Retry Parameters

```python
ForEach(
    retries: Optional[AsyncRetrying] = None,
    concurrency: Optional[object] = None,
    storage: Optional[Storage] = None,
)
```

**Parameters:**

- `retries` (AsyncRetrying, optional): Custom retry configuration using tenacity's `AsyncRetrying` class. If not provided, uses default retry behavior (3 attempts with exponential backoff)
- `concurrency` (object, optional): Concurrency strategy (`SlidingWindow` or `Adaptive`). Defaults to `Adaptive()` for async functions
- `storage` (Storage, optional): Custom storage backend for persisting evaluation results

#### AsyncRetrying Configuration

The `AsyncRetrying` class from tenacity supports these common parameters:

```python
AsyncRetrying(
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=60),
    reraise=True,
)
```

**Common Parameters:**

- `retry`: Condition for when to retry (e.g., `retry_if_exception_type`, `retry_if_result`)
- `stop`: When to stop retrying (e.g., `stop_after_attempt`, `stop_after_delay`)
- `wait`: Wait strategy between retries (e.g., `wait_fixed`, `wait_exponential`, `wait_exponential_jitter`)
- `reraise` (bool, default=True): Whether to reraise the exception after all retries are exhausted

## Error Handling

Async evaluations provide automatic error handling:

```python
@dotevals.foreach("question,answer", dataset)
async def eval_with_errors(question, answer, model):
    try:
        result = await model.generate(question)
        return exact_match(result, answer)
    except Exception as e:
        # Error is captured automatically
        raise e
```


## See Also

### Core Concepts
- **[@foreach Decorator](foreach.md)** - Learn how to create async evaluations using `@foreach` with `async def`
- **[Experiments](experiments.md)** - Understand how async evaluations integrate with experiment management and resumption

### Integration Guides
- **[Pytest Integration](pytest.md)** - Run async evaluations through pytest with command-line concurrency control
- **[CLI Reference](cli.md)** - Control async evaluation execution with `--concurrent` and other CLI options

### Advanced Usage
- **[Evaluators](evaluators.md)** - Use evaluators within async evaluation contexts for performance optimization
- **[Metrics](metrics.md)** - Compute metrics from async evaluation results
- **[Storage Backends](storage.md)** - Handle data persistence with concurrent async workloads

### Tutorials
- **[Scale with Async Evaluation](../tutorials/05-scale-with-async-evaluation.md)** - Transform slow sync evaluations into fast async ones
- **[Build a Production Evaluation Pipeline](../tutorials/08-build-production-evaluation-pipeline.md)** - Design scalable async evaluation systems
