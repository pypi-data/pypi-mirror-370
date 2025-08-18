# Data Handling

dotevals provides flexible data handling capabilities for various dataset formats and sources.

## Streaming-First Architecture

**dotevals is streaming-first** - it processes datasets one item at a time without loading everything into memory. This means you can evaluate on datasets that don't fit in memory, including:

- Multi-gigabyte datasets streamed from disk
- Live data from APIs or databases
- Infinite generators that produce data on-demand
- Large HuggingFace datasets with streaming enabled

## Overview

dotevals supports:

- Multiple dataset formats (lists, tuples, iterators, generators)
- Built-in registered datasets with `@foreach.dataset_name()` syntax
- HuggingFace Datasets integration with streaming
- Custom column mappings

## Basic Dataset Formats

### Lists and Tuples

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

# Simple question-answer pairs
dataset = [
    ("What is 2+2?", "4"),
    ("What is 3+3?", "6")
]

@foreach("question,answer", dataset)
def eval_simple(question, answer, model):
    result = model.generate(question)
    return exact_match(result, answer)
```

### Single Column Datasets

```python
from dotevals import foreach

prompts = [("Write a poem",), ("Explain gravity",)]

@foreach("prompt", prompts)
def eval_single_column(prompt, model):
    result = model.generate(prompt)
    # Return your custom quality score evaluation
    return quality_score(result)
```

### Multi-Column Datasets

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

dataset = [
    ("context1", "question1", "answer1"),
    ("context2", "question2", "answer2")
]

@foreach("context,question,answer", dataset)
def eval_multi_column(context, question, answer, model):
    prompt = f"Context: {context}\nQuestion: {question}"
    result = model.generate(prompt)
    return exact_match(result, answer)
```





## Column Specification

Column names in the `@foreach` decorator must match the dataset structure:

```python
# Dataset: (context, question, answer)
dataset = [
    ("The sky is blue.", "What color is the sky?", "blue"),
    ("E=mc²", "What is Einstein's equation?", "E=mc²")
]

@dotevals.foreach("context,question,answer", dataset)
def eval_with_context(context, question, answer, model):
    prompt = f"Context: {context}\nQuestion: {question}"
    result = model.generate(prompt)
    return exact_match(result, answer)
```

## Dataset Iterator Requirements

Any dataset provided to `@foreach` must satisfy these requirements:

### Iterator Protocol
```python
def custom_dataset() -> Iterator[Tuple]:
    """Custom dataset generator function"""
    pass
```

**Requirements:**
- Must implement the iterator protocol (`__iter__` and `__next__`)
- Each iteration must yield a tuple with consistent structure
- Tuple length must match the number of columns specified in `@foreach`
- Can be finite (list, tuple) or infinite (generator, stream)

### Tuple Structure
```python
# Single column: each item is a 1-tuple
dataset = [("prompt1",), ("prompt2",)]

# Multiple columns: each item is an n-tuple
dataset = [("input1", "output1"), ("input2", "output2")]

# Dict-like access (convert to tuple)
def dict_to_tuple_dataset(dict_dataset):
    for item in dict_dataset:
        yield (item["input"], item["output"])
```

**Requirements:**
- All tuples must have the same length within a dataset
- Tuple order must match the column order in `@foreach("col1,col2,col3", dataset)`
- Values can be any Python object (strings, images, complex structures)


## See Also

### Core Concepts
- **[@foreach Decorator](foreach.md)** - Master column specifications and dataset integration with `@foreach`
- **[Evaluators](evaluators.md)** - Apply data validation patterns and preprocessing for robust evaluations

### Integration Guides
- **[Experiments](experiments.md)** - Understand how dataset processing integrates with experiment management
- **[Async Evaluations](async.md)** - Process large datasets efficiently with async evaluation patterns

### Advanced Usage
- **[Storage Backends](storage.md)** - Optimize storage for different dataset sizes and formats
- **[Pytest Integration](pytest.md)** - Use pytest fixtures for dataset loading and management

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with simple dataset formats
- **[Working with Real Datasets](../tutorials/03-working-with-real-datasets.md)** - Load and process real-world datasets effectively
- **[Build a Production Evaluation Pipeline](../tutorials/08-build-production-evaluation-pipeline.md)** - Design robust data pipelines for production systems
