# Evaluators

Evaluators are the core components that score model outputs against expected results. They define the criteria by which you measure your model's performance.

## Plugin System

Evaluators can be distributed as plugins and automatically discovered via Python entry points. When you import from `dotevals.evaluators`, the system automatically loads all registered evaluator plugins.

**Installing Evaluator Plugins:**
```bash
pip install dotevals-evaluators-extended
```

Once installed, plugin evaluators are automatically available:
```python
from dotevals.evaluators import fuzzy_match, semantic_similarity  # From plugin
```

## Built-in Evaluators

### exact_match

The `exact_match` evaluator checks for exact string equality between the model output and expected result.

```python
from dotevals.evaluators import exact_match

# Simple usage
score = exact_match("42", "42")  # Returns Score(name="exact_match", value=True, metrics=[accuracy()], metadata={...})

# With custom name
score = exact_match("42", "42", name="math_match")  # Returns Score with name="math_match"

# In an evaluation
@foreach("question,answer", dataset)
def eval_math(question, answer, model):
    result = model.generate(question)
    return exact_match(result, answer)
```

### numeric_match

The `numeric_match` evaluator compares numeric values, automatically handling various formats like thousand separators (commas and spaces), scientific notation, and leading/trailing zeros.

```python
from dotevals.evaluators import numeric_match

# Different formats that are considered equal
numeric_match("1234", "1,234")      # True - comma separator
numeric_match("1234", "1 234")      # True - space separator
numeric_match("1234", "1.234e3")    # True - scientific notation
numeric_match("42.0", "42")         # True - trailing zeros
numeric_match("0.50", "0.5")        # True - trailing zeros

# In an evaluation - perfect for math problems
@foreach("problem,solution", math_dataset)
def eval_math(problem, solution, model):
    result = model.generate(problem)
    # Handles cases where model outputs "1,234" but answer is "1234"
    return numeric_match(result, solution)
```

This evaluator is particularly useful for mathematical evaluations where the model might format numbers differently than the expected answer.

### valid_json

The `valid_json` evaluator checks if a value is valid JSON and optionally validates it against a JSON schema.

```python
from dotevals.evaluators import valid_json

# Check if string is valid JSON
valid_json('{"name": "John"}')      # True
valid_json('["a", "b", "c"]')       # True
valid_json('123')                   # True - valid JSON number
valid_json('{"name": "John",}')     # False - trailing comma
valid_json('invalid')               # False

# With JSON schema validation
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    },
    "required": ["name"]
}

valid_json('{"name": "John", "age": 30}', schema)  # True
valid_json('{"age": 30}', schema)                  # False - missing required field
valid_json('{"name": "John", "age": "thirty"}', schema)  # False - wrong type

# In an evaluation - perfect for structured output validation
@foreach("prompt,expected_schema", dataset)
def eval_structured_output(prompt, expected_schema, model):
    result = model.generate(prompt, response_format="json")
    return valid_json(result, expected_schema)
```

This evaluator is ideal for validating structured outputs from LLMs, especially when using JSON mode or when expecting specific data formats.

## Creating Custom Evaluators

Use the `@evaluator` decorator to create custom scoring functions with associated metrics.

### Basic Custom Evaluator

```python
from dotevals.evaluators import evaluator
from dotevals.metrics import accuracy  # See Metrics reference for more options

@evaluator(metrics=accuracy())
def contains_keyword(response: str, keyword: str) -> bool:
    """Check if response contains a specific keyword."""
    return keyword.lower() in response.lower()

# Usage
@foreach("prompt,expected_keyword", dataset)
def eval_keyword_presence(prompt, expected_keyword, model):
    response = model.generate(prompt)
    return contains_keyword(response, expected_keyword)
```

### Multi-Metric Evaluator

Attach multiple metrics to a single evaluator:

```python
from dotevals.metrics import accuracy, metric

@metric
def precision() -> Metric:
    def calculate(scores: list[bool]) -> float:
        true_positives = sum(scores)
        predicted_positives = len(scores)
        return true_positives / predicted_positives if predicted_positives > 0 else 0.0
    return calculate

@evaluator(metrics=[accuracy(), precision()])
def sentiment_match(predicted: str, expected: str) -> bool:
    """Evaluate sentiment classification accuracy."""
    return predicted.strip().lower() == expected.strip().lower()
```

### Custom Evaluators with Logic

```python
import re

@evaluator(metrics=accuracy())
def extract_answer_evaluator(response: str, expected: str) -> bool:
    """Extract and compare numerical answers."""
    # This pattern matches "answer is 42", "answer: 42", "result = 42", etc.
    pattern = r"(?:answer|result).*?(\d+(?:\.\d+)?)"
    match = re.search(pattern, response.lower())

    if not match:
        return False

    return match.group(1) == expected.strip()
```

### Comparative Evaluators

```python
@evaluator(metrics=accuracy())
def preference_evaluator(response_a: str, response_b: str, preference: str) -> bool:
    """Compare two responses based on preference."""
    # Your comparison logic here
    return (preference == "A" and quality_score(response_a) > quality_score(response_b)) or \
           (preference == "B" and quality_score(response_b) > quality_score(response_a))
```

## Working with Scores

Evaluators return `Score` objects that contain:

- **name**: The evaluator function name
- **value**: The evaluation result (typically bool, float, or str)
- **metrics**: List of metrics to compute
- **metadata**: Additional context about the evaluation

```python
from dotevals.evaluators import exact_match

score = exact_match("hello", "hello")
print(f"Evaluator: {score.name}")         # "exact_match"
print(f"Result: {score.value}")           # True
print(f"Metrics: {score.metrics}")        # [<function accuracy at 0x...>]
print(f"Metadata: {score.metadata}")      # {"result": "hello", "expected": "hello"}
```




## Creating Evaluator Plugins

To distribute custom evaluators as a plugin that can be imported from `dotevals.evaluators`, see [How to Create an Evaluator Plugin](../how-to/plugins/create-evaluator-plugin.md).

## See Also

### Core Concepts
- **[Metrics](metrics.md)** - Learn how to create and attach metrics to evaluators for result aggregation
- **[@foreach Decorator](foreach.md)** - Understand how evaluators integrate with `@foreach` decorated evaluation functions
- **[Data Handling](datasets.md)** - Explore data validation patterns and preprocessing techniques for evaluators

### Integration Guides
- **[Experiments](experiments.md)** - See how evaluator results are stored and managed in evaluation experiments
- **[Async Evaluations](async.md)** - Use evaluators in async evaluation contexts for better performance

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with built-in evaluators like `exact_match`
- **[Building Custom Evaluators](../tutorials/04-building-custom-evaluators.md)** - Step-by-step guide to creating sophisticated custom evaluators
- **[Using Real Models](../tutorials/02-using-real-models.md)** - Apply evaluators to real model outputs in practice

### How-To Guides
- **[How to Create an Evaluator Plugin](../how-to/plugins/create-evaluator-plugin.md)** - Create and distribute custom evaluators as plugins
