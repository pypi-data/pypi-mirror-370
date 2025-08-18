# Core Terminology

This glossary defines the key terms and concepts used throughout dotevals documentation.

### **Evaluation**
The process of systematically testing an LLM's performance on a specific task using a dataset and scoring criteria.

An evaluation consists of:

1. A dataset (test cases)
2. A model to test
3. Evaluators (scoring functions)
4. Metrics (aggregation methods)

### **Dataset**
A collection of test cases used to evaluate model performance. Each item typically contains input data and expected outputs. Datasets can be provided through plugins for standard benchmarks.

```python
dataset = [
    ("What is 2+2?", "4"),           # Tuple format
    {"prompt": "Hi", "expected": "Hello"},  # Dict format
]
```

See [Available Plugins](../reference/plugins.md#dotevals-datasets) for dataset plugins like GSM8K.

### **Evaluator**
A function that scores a model's output against expected results. Returns a Score object. Additional evaluators can be added through plugins for specialized evaluation methods.

```python
from dotevals.evaluators import exact_match

score = exact_match(model_output="Paris", expected="Paris")
# Returns: Score(value=True, ...)
```

See [Available Plugins](../reference/plugins.md#dotevals-evaluators-llm) for advanced evaluators.

### **Metric**
A function that aggregates multiple scores into a single numerical value.

```python
from dotevals.metrics import accuracy

# Given scores: [True, True, False, True]
result = accuracy([True, True, False, True])  # Returns: 0.75
```

### **Score**
The result of an evaluator, containing the evaluation outcome and metadata.

```python
Score(
    name="exact_match",
    value=True,  # The evaluation result
    metrics=[accuracy()],  # Associated metrics
    metadata={"model_output": "Paris", "expected": "Paris"}
)
```

### **Result**
A container for model output and evaluation scores, used within evaluation functions.

```python
from dotevals import Result

return Result(
    prompt="What is 2+2?",
    output="4",
    scores=[exact_match_score]
)
```

### **Experiment**
A named collection of related evaluations. Useful for organizing and comparing different evaluation runs.

```python
# Running evaluations in an experiment:
pytest eval.py --experiment "gpt4_vs_claude"
```

### **Session**
A single execution run of evaluations. An experiment can span multiple sessions when evaluations are resumed after interruption or run incrementally over time.

### **Storage Backend**
Where evaluation results are saved. Can be JSON files, SQLite databases, or custom storage. Additional storage backends can be added through plugins for different databases and cloud storage.

```python
from dotevals.storage import get_storage

storage = get_storage("json://./results")  # JSON storage
```

See [Available Plugins](../reference/plugins.md#dotevals-storage-sqlite) for storage plugins.

### **Model Provider**
A source of LLM functionality (OpenAI, Anthropic, Hugging Face, etc.). Model providers can be added through plugins to support different LLM services and deployment methods.

See [Available Plugins](../reference/plugins.md#official-plugins) for model provider plugins.


## Next steps

- **Ready to start coding?** Follow the [Quickstart Guide](../quickstart.md)
- **Want to understand the architecture?** See [Design Principles](../explanation/design-principles.md)
