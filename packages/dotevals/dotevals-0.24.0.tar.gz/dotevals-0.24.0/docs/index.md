---
title: dotevals
hide:
  - navigation
  - toc
  - feedback
---

#

<div class="index-container" markdown style="max-width: 800px; margin: 0 auto;">

<figure markdown>
  ![dotevals](assets/images/dotevals.svg){ width="200" }
</figure>

<center>
    <h1 class="title">Write Once, Evaluate Anywhere</h1>
    <p class="subtitle">The Python evaluation framework for notebooks and production</p>

    <a href="welcome.md">Get started</a> • <a href="https://github.com/dottxt-ai/dotevals">View on GitHub</a>

<div class="index-pre-code">
```bash
pip install dotevals
```
</div>
</center>

---

## Quick Example

Evaluate your model on a simple dataset in just a few lines:

```python title="eval_math.py"
from dotevals import foreach
from dotevals.evaluators import exact_match

# Your dataset (or load from HuggingFace)
dataset = [
    ("What is 2 + 2?", "4"),
    ("What is 5 × 3?", "15"),
    ("What is 10 - 7?", "3"),
]

@foreach("question,answer", dataset)
def eval_math(question, answer, model):
    """Evaluate model performance on math problems."""
    result = model.generate(question)
    return exact_match(result, answer)
```

=== "Interactive"

    ```python title="In a notebook or script"
    from dotevals import run

    # Run evaluation and get results
    results = run(eval_math, model=my_model)

    # View summary
    print(results.summary())
    ```

=== "Pytest"

    Run it with pytest:

    ```bash
    pytest eval_math.py::eval_math --experiment math_eval
    ```

    View results:

    ```bash
    dotevals show math_eval
    ```

## Why dotevals?

### :fontawesome-solid-code: Simple API

Define evaluations with just a decorator. No complex setup required.

```python
@foreach("question,answer", dataset)
def eval_model(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

### :fontawesome-solid-laptop-code: Write Once, Run Anywhere

Develop and debug evaluations interactively in notebooks, then run the exact same code in CI/CD pipelines. Get immediate feedback with inline results and summaries.

```python
# Same evaluation works in notebooks and pytest
results = run(eval_model, model=my_model)
print(results.summary())  # {'total': 100, 'errors': 0, 'metrics': {...}}
```

### :fontawesome-solid-flask: pytest Integration

Leverage the full pytest ecosystem - use fixtures for resource management, parametrize evaluations across models, apply markers for test organization, and integrate with your existing CI/CD pipelines.

```python
@pytest.fixture
def model():
    """Reusable model fixture."""
    return load_model()

@pytest.mark.parametrize("model_name", ["gpt-3.5", "gpt-4"])
@foreach("question,answer", dataset)
def eval_compare(question, answer, model_name):
    """Compare multiple models."""
    # ...
```

### :fontawesome-solid-clock-rotate-left: Automatic Resumption

Resume interrupted evaluations automatically. Never lose progress due to crashes or timeouts - dotevals tracks every completed sample and picks up exactly where it left off.

### :fontawesome-solid-bolt: Scalable

Handle evaluations from 10 to 10,000+ samples with built-in async support and sophisticated concurrency control. Easily scale from local development to distributed cloud execution.

---

## Documentation

<div class="grid cards" markdown>

-   :fontawesome-solid-rocket: **[Getting Started](welcome.md)**

    ---

    New to dotevals? Start here for installation, quickstart, and core concepts.

-   :fontawesome-solid-graduation-cap: **[Tutorials](tutorials/01-your-first-evaluation.md)**

    ---

    Step-by-step guides from your first evaluation to production deployment.

-   :fontawesome-solid-wrench: **[How-To Guides](how-to/index.md)**

    ---

    Problem-focused guides for structured generation, debugging, and production issues.

-   :fontawesome-solid-book: **[Reference](reference/index.md)**

    ---

    Complete API documentation and technical reference materials.

</div>

---

<div class="footer-info">
<center>
Built with ❤️ by <a href="https://dottxt.co">dottxt</a> • <a href="https://github.com/dottxt-ai/dotevals">GitHub</a> • <a href="https://pypi.org/project/dotevals/">PyPI</a>
</center>
</div>

</div>
