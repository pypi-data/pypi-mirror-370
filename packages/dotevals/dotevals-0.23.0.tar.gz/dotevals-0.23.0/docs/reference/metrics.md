# Metrics

Metrics aggregate evaluation results to provide meaningful performance measurements. They transform lists of individual evaluation results into single numerical scores that help you understand your model's overall performance.

## Metrics API Reference

### Type Definitions

**`Metric = Callable[[List[bool]], float]`**

Type alias for metric functions. A metric is a callable that:

- Takes a list of boolean evaluation results
- Returns a single float score (typically 0.0 to 1.0)
- Aggregates individual results into a summary statistic

### Core Decorator

#### `@metric`

```python
@metric
def metric_func(arg1: Type1, arg2: Type2, ...) -> Metric:
    # Function body that returns a Metric callable
    pass
```

Decorator for creating metric functions that can be attached to evaluators.

**Function Signature:**
```python
metric(metric_func: Callable[..., Metric]) -> Callable[..., Metric]
```

**Parameters:**

- `metric_func` (`Callable[..., Metric]`): Function that returns a metric callable
  - The function can accept any parameters for configuration
  - Must return a function with signature `(List[bool]) -> float`
  - Function name is used for metric identification and serialization

**Returns:**

- `Callable[..., Metric]`: Wrapper function that creates metric instances

**Behavior:**

- Registers the metric in the global registry for serialization
- Preserves the original function name for identification
- Enables parameterized metrics through the decorator pattern

**Examples:**
```python
from dotevals.metrics import metric

# Simple metric (no parameters)
@metric
def pass_rate() -> Metric:
    def calculate(scores: List[bool]) -> float:
        return sum(scores) / len(scores) if scores else 0.0
    return calculate

# Parameterized metric
@metric
def weighted_accuracy(weights: List[float]) -> Metric:
    def calculate(scores: List[bool]) -> float:
        if not scores or len(scores) != len(weights):
            return 0.0
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    return calculate

# Usage
basic_metric = pass_rate()
weighted_metric = weighted_accuracy([1.0, 2.0, 1.5])

# Both can be attached to evaluators
@evaluator(metrics=[basic_metric, weighted_metric])
def my_evaluator(predicted, expected):
    return predicted == expected
```

## How Metrics Work

Metrics are functions that take a list of evaluation results and return a single aggregated score. They are attached to evaluators and computed automatically when evaluations complete.

```python
from dotevals.metrics import accuracy

# Create metric instance
accuracy_metric = accuracy()

# This metric function receives a list of boolean values
# and returns the percentage that are True
score = accuracy_metric([True, False, True, True])  # Returns 0.75
```

## Built-in Metrics

### Built-in Metrics

#### `accuracy() -> Metric`

The `accuracy` metric calculates the percentage of correct results. It's the most commonly used metric for classification and exact-match tasks.

**Function Signature:**
```python
@metric
def accuracy() -> Metric:
    def metric(scores: List[bool]) -> float:
        # Implementation details...
    return metric
```

**Parameters:**

- None (parameter-free metric)

**Returns:**

- `Metric`: Function that takes `List[bool]` and returns accuracy as `float`

**Behavior:**
- **Input**: List of boolean evaluation results
- **Output**: Fraction of `True` values (range: `[0.0, 1.0]`)
- **Empty list**: Returns `0.0`
- **Calculation**: `sum(True_values) / total_count`

**Examples:**
```python
from dotevals.metrics import accuracy
from dotevals.evaluators import evaluator

# Create accuracy metric instance
accuracy_metric = accuracy()

# Direct usage
result = accuracy_metric([True, False, True, True])  # Returns 0.75
result = accuracy_metric([])  # Returns 0.0
result = accuracy_metric([True, True, True])  # Returns 1.0

# Usage with evaluators
@evaluator(metrics=accuracy())
def exact_match(predicted: str, expected: str) -> bool:
    """Check exact string match."""
    return predicted.strip() == expected.strip()

# When evaluation runs, accuracy will be computed automatically:
# accuracy([True, False, True, True]) = 0.75 (75% accuracy)
```

**Metric Properties:**

- **Type**: Classification/binary accuracy metric
- **Range**: `[0.0, 1.0]` where 1.0 is perfect accuracy
- **Empty handling**: Returns 0.0 for empty result lists
- **Performance**: O(n) time complexity, O(1) space complexity

## Creating Custom Metrics

Use the `@metric` decorator to create custom aggregation functions.

### Basic Custom Metric

```python
from dotevals.metrics import metric
from dotevals.evaluators import evaluator

@metric
def error_rate() -> Metric:
    """Calculate the error rate (opposite of accuracy)."""
    def calculate(scores: list[bool]) -> float:
        if len(scores) == 0:
            return 0.0
        return 1.0 - (sum(scores) / len(scores))
    return calculate

@evaluator(metrics=[accuracy(), error_rate()])
def spelling_check(text: str, expected: str) -> bool:
    return text.lower().strip() == expected.lower().strip()
```

### Statistical Metrics

```python
@metric
def precision() -> Metric:
    """Calculate precision for binary classification."""
    def calculate(results: list[bool]) -> float:
        if not results:
            return 0.0
        return sum(results) / len(results)
    return calculate

@evaluator(metrics=[accuracy(), precision()])
def classification_evaluator(predicted: str, actual: str) -> bool:
    return predicted == actual
```

### Numerical Metrics

```python
@metric
def mean_absolute_error() -> Metric:
    """Calculate mean absolute error."""
    def calculate(errors: list[float]) -> float:
        if not errors:
            return 0.0
        return sum(abs(error) for error in errors) / len(errors)
    return calculate

@evaluator(metrics=[mean_absolute_error()])
def numerical_evaluator(predicted: str, expected: str) -> float:
    return abs(float(predicted) - float(expected))
```

### Text Metrics

```python
@metric
def average_length() -> Metric:
    """Calculate average text length."""
    def calculate(texts: list[str]) -> float:
        if not texts:
            return 0.0
        return sum(len(text) for text in texts) / len(texts)
    return calculate

@evaluator(metrics=[average_length()])
def text_evaluator(response: str) -> str:
    return response  # Metric will calculate length
```

### Aggregation Metrics

```python
@metric
def any_correct() -> Metric:
    """Return 1.0 if any evaluation is correct."""
    def calculate(scores: list[bool]) -> float:
        return 1.0 if any(scores) else 0.0
    return calculate

@metric
def all_correct() -> Metric:
    """Return 1.0 if all evaluations are correct."""
    def calculate(scores: list[bool]) -> float:
        return 1.0 if all(scores) else 0.0
    return calculate
```

## Multiple Metrics per Evaluator

Attach multiple metrics to a single evaluator for comprehensive analysis:

```python
@evaluator(metrics=[accuracy(), error_rate(), any_correct(), all_correct()])
def comprehensive_match(predicted: str, expected: str) -> bool:
    """Evaluate with multiple metrics."""
    return predicted.strip().lower() == expected.strip().lower()

# This will compute all four metrics:
# - accuracy: percentage of correct matches
# - error_rate: percentage of incorrect matches
# - any_correct: 1.0 if at least one match is correct
# - all_correct: 1.0 if all matches are correct
```

## Parameterized Metrics

```python
@metric
def threshold_accuracy(threshold: float = 0.5) -> Metric:
    """Accuracy for scores above threshold."""
    def calculate(scores: list[float]) -> float:
        if not scores:
            return 0.0
        above_threshold = [score >= threshold for score in scores]
        return sum(above_threshold) / len(above_threshold)
    return calculate

# Use with custom threshold
@evaluator(metrics=[threshold_accuracy(0.8)])
def confidence_evaluator(prediction: str, expected: str) -> float:
    return calculate_similarity(prediction, expected)
```

## Metric Registry and Plugin System

dotevals maintains a global registry of metrics for serialization, deserialization, and storage. The registry supports automatic discovery of metrics from installed plugins.

### Plugin Discovery

Metrics can be distributed as plugins and automatically discovered via Python entry points. When you import from `dotevals.metrics`, the system automatically loads all registered metric plugins.

**Installing Metric Plugins:**
```bash
pip install dotevals-metrics-extended
```

Once installed, plugin metrics are automatically available:
```python
from dotevals.metrics import weighted_accuracy, harmonic_mean  # From plugin
```

### Registry Structure

**`registry: dict[str, Metric]`**

Global dictionary mapping metric names to metric instances.

**Structure:**
```python
registry = {
    "accuracy": accuracy(),  # Built-in metrics
    "custom_metric": custom_metric(),  # User-defined metrics
    "weighted_accuracy": weighted_accuracy(),  # Plugin metrics
    # ... additional registered metrics
}
```

### Registry Usage

**Accessing the Registry:**
```python
from dotevals.metrics import registry

# List all registered metric names
available_metrics = list(registry.keys())
print(f"Available metrics: {available_metrics}")  # ['accuracy']

# Get specific metric instance
accuracy_instance = registry["accuracy"]
result = accuracy_instance([True, False, True])  # 0.667

# Check if metric exists
if "accuracy" in registry:
    print("Accuracy metric is available")
```

**Automatic Registration:**
Metrics are automatically registered when defined with `@metric`:

```python
@metric
def f1_score() -> Metric:
    def calculate(scores: list[bool]) -> float:
        # F1 score implementation
        return sum(scores) / len(scores) if scores else 0.0
    return calculate

# Automatically added to registry
print("f1_score" in registry)  # True
f1_instance = registry["f1_score"]
```

**Registry Applications:**

- **Serialization**: Store metric names in evaluation results
- **Deserialization**: Recreate metric instances from stored names
- **Discovery**: List available metrics programmatically
- **Validation**: Verify metric availability before use

**Built-in Registered Metrics:**

- `"accuracy"`: Built-in accuracy metric instance

**Example: Using Registry for Dynamic Metrics:**
```python
from dotevals.metrics import registry

def create_evaluator_with_metrics(metric_names: list[str]):
    """Create evaluator with metrics by name."""
    metrics = [registry[name] for name in metric_names if name in registry]

    @evaluator(metrics=metrics)
    def dynamic_evaluator(predicted, expected):
        return predicted == expected

    return dynamic_evaluator

# Usage
evaluator_func = create_evaluator_with_metrics(["accuracy", "f1_score"])
```

## Working with Evaluation Results

Metrics receive the raw evaluation results from evaluators:

```python
from dotevals import foreach
from dotevals.evaluators import evaluator
from dotevals.metrics import accuracy

@evaluator(metrics=accuracy())
def sentiment_match(predicted: str, expected: str) -> bool:
    """Simple sentiment matching."""
    return predicted.lower().strip() == expected.lower().strip()

@foreach("text,sentiment", sentiment_dataset)
def eval_sentiment(text, sentiment, model):
    prediction = model.classify_sentiment(text)
    return sentiment_match(prediction, sentiment)

# When evaluation completes:
# 1. sentiment_match returns True/False for each sample
# 2. All boolean results are collected into a list
# 3. accuracy() receives this list: [True, False, True, False, ...]
# 4. accuracy() returns the fraction of True values
```


## Creating Metric Plugins

To distribute custom metrics as a plugin that can be imported from `dotevals.metrics`, see [How to Create a Metrics Plugin](../how-to/plugins/create-metrics-plugin.md).

## See Also

### Core Concepts
- **[Evaluators](evaluators.md)** - Learn how to attach metrics to evaluators for automatic computation
- **[Experiments](experiments.md)** - Understand how metrics are computed and stored in evaluation experiments

### Integration Guides
- **[@foreach Decorator](foreach.md)** - See how metrics integrate with `@foreach` decorated evaluation functions
- **[Async Evaluations](async.md)** - Use metrics with async evaluations for performance insights

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with built-in metrics like `accuracy()`
- **[Building Custom Evaluators](../tutorials/04-building-custom-evaluators.md)** - Learn to create custom metrics for specialized evaluation criteria
- **[Comparing Multiple Models](../tutorials/07-comparing-multiple-models.md)** - Use metrics to compare model performance across different configurations

### How-To Guides
- **[How to Create a Metrics Plugin](../how-to/plugins/create-metrics-plugin.md)** - Create and distribute custom metrics as plugins
