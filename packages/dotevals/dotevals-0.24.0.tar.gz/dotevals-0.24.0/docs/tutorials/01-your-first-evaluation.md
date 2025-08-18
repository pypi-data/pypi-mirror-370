# Tutorial 1: Your First Evaluation

In this tutorial, you'll create and run your first LLM evaluation with dotevals in about 10 minutes.

## What you'll learn

- How to install and set up dotevals
- How to create a basic evaluation with `@foreach`
- How to run evaluations and view results
- How to manage experiments for tracking progress

## Install dotevals

```bash
pip install dottxt-eval
```

## Create Your First Evaluation

Create a file called `eval_math.py`:

```python title="eval_math.py"
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

# Simple math problems dataset
math_data = [
    ("What is 2 + 3?", "5"),
    ("What is 10 - 4?", "6"),
    ("What is 3 * 2?", "6"),
]

@foreach("question,answer", math_data)
def eval_basic_math(question, answer):
    """Test basic math problem solving."""
    # Simulate a model that gets most answers right
    if "2 + 3" in question:
        prediction = "5"
    elif "10 - 4" in question:
        prediction = "6"
    else:
        prediction = "7"  # Wrong answer for 3 * 2

    return Result(
        exact_match(prediction, answer),
        prompt=question
    )
```

## Run the Evaluation

```bash
pytest eval_math.py --experiment my_first_eval
```

You'll see output like:

```
============================= test session starts ==============================
platform darwin -- Python 3.11.11, pytest-8.4.1, pluggy-1.6.0
rootdir: /your/project
plugins: asyncio-1.1.0, dotevals-0.1.dev69+g65c8b0a, cov-6.2.1
collected 1 item

eval_math.py .

[100%]✨ eval_basic_math[None-None] ━━━━━━━━━━ 3/3 • Elapsed: 0:00:00 • ETA: 0:00:00

============================== 1 passed in 0.02s ===============================
```

## View Results

```bash
dotevals show my_first_eval
```

This shows the aggregated results:

```
       Summary of my_first_eval ::
          eval_basic_math[None-None]

  Evaluator     Metric     Score       Errors
 ─────────────────────────────────────────────
  exact_match   accuracy    0.67   0/3 (0.0%)
```

The accuracy of 0.67 means 2 out of 3 questions were answered correctly (66.7%).

!!! info "Understanding 'Errors' in the summary"
    The "Errors" column shows **technical failures** during evaluation (e.g., API timeouts, network issues, or code exceptions) - not wrong answers from the model. In this example, "0/3 (0.0%)" means all 3 evaluations ran successfully without technical issues. The model getting 1 answer wrong is reflected in the Score (0.67), not in Errors.

## Understanding the Code

- **`@foreach`**: Turns your function into an evaluation that runs on each data item
- **`Result`**: Wraps your evaluation output with the prompt and scores
- **`exact_match`**: Built-in evaluator that checks if two strings are identical
- **Experiments**: Named evaluations (like `my_first_eval`) that save your results

## Managing Experiments

List all your experiments:

```bash
dotevals list
```

Run a new experiment:

```bash
pytest eval_math.py --experiment math_v2
```

Compare results by viewing different experiments.

## Next Steps

**[Tutorial 2: Using Real Models](02-using-real-models.md)** - Connect to OpenAI, local models, and handle real APIs

The key insight: dotevals makes LLM evaluation as simple as writing pytest tests.

## See Also

- **[How-To Guides](../how-to/index.md)** - Problem-focused guides for specific challenges
- **[Reference: Experiments](../reference/experiments.md)** - Technical details on experiment management
- **[Reference: CLI](../reference/cli.md)** - Complete `dotevals` command reference
