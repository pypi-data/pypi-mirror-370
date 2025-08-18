# Tutorial 4: Build Custom Evaluators

In this tutorial, you'll build a custom LLM judge evaluator that scores creative writing on multiple criteria.

## What you'll learn

- How to create custom evaluators with `@evaluator`
- How to design effective LLM judge prompts
- How to parse and structure LLM responses
- How to return multi-metric evaluation results
- How to iterate and improve evaluator reliability

## Why Use LLM Judges?

LLM judges are powerful tools for evaluating subjective qualities that traditional metrics can't capture. While exact match or BLEU scores work well for factual correctness, they fail to assess creativity, coherence, helpfulness, or style. LLM judges can be useful in these situations.

For example, determining if a story is "engaging" requires understanding narrative flow, character development, and emotional resonance - tasks where LLMs shine. By crafting clear prompts with specific criteria, you can create reliable automated evaluators for complex, subjective tasks.

## Step 1: Understanding Prompt Engineering Principles

Before creating LLM judges, let's understand the key principles of effective prompt engineering.

### Core Prompt Design Principles

**1. Be Specific and Clear**
```python
# ❌ Vague prompt
"Rate this story."

# ✅ Specific prompt
"Rate this creative writing story on a scale of 1-10 for creativity, coherence, and grammar."
```

**2. Provide Structure and Format**
```python
# ❌ Unstructured output
"Tell me what you think about this story."

# ✅ Structured output
"Provide ratings in this exact format:
creativity: [score], coherence: [score], grammar: [score]"
```

**3. Include Examples**
```python
# ❌ No examples
"Rate the story."

# ✅ With examples
"Rate the story like this example:
creativity: 8, coherence: 7, grammar: 9"
```

**4. Define Your Criteria**
```python
# ❌ Undefined criteria
"Rate creativity."

# ✅ Defined criteria
"CREATIVITY (1=cliché, 10=highly original):
- Unique ideas, unexpected elements, imaginative concepts"
```

### Response Parsing Patterns

When working with LLM outputs, you'll encounter the need to write robust functions to parse the output:

```python
def parse_key_value_pairs(response: str) -> dict:
    """Parse 'key: value' format responses.

    Handles variations like:
    - Extra whitespace: "creativity : 8"
    - Mixed case: "Creativity: 8"
    - Multiple colons: "Note: creativity: 8"
    """
    result = {}
    for line in response.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)  # split only on first colon
            result[key.strip().lower()] = value.strip()
    return result

def parse_comma_separated(response: str) -> dict:
    """Parse 'key1: value1, key2: value2' format.

    Handles single-line responses with multiple metrics.
    """
    result = {}
    for part in response.split(','):
        if ':' in part:
            key, value = part.split(':')
            result[key.strip().lower()] = value.strip()
    return result

def safe_int_conversion(value: str, default: int = 0) -> int:
    """Safely convert strings to integers.

    Essential because LLMs might return:
    - "8" (correct)
    - "8/10" (needs extraction)
    - "eight" (needs default)
    - "8.5" (needs rounding)
    """
    try:
        # Handle "8/10" format
        if '/' in value:
            value = value.split('/')[0]
        # Handle decimals
        return int(float(value.strip()))
    except (ValueError, AttributeError):
        return default
```

!!! warning "Why parsing functions are critical"
    LLMs are text generators, not structured data APIs. Even with the clearest prompts, they might:

    - Add extra explanation text around your requested format
    - Use slightly different formatting (e.g., "creativity:8" vs "creativity: 8" vs "Creativity: 8")
    - Include line breaks or extra whitespace
    - Occasionally deviate from the requested format entirely

    **Robust parsing functions are your safety net** - they extract the data you need even when the LLM's response isn't perfect. Without them, your evaluations will crash on minor formatting variations.

    Example of real LLM responses you might encounter:
    ```
    # What you asked for:
    "creativity: 8, coherence: 7, grammar: 9"

    # What you might actually get:
    "Let me evaluate this story. Creativity: 8, Coherence: 7, Grammar: 9"
    "creativity: 8\ncoherence: 7\ngrammar: 9"
    "Creativity: 8/10, Coherence: 7/10, Grammar: 9/10"
    ```

!!! tip "A better approach: Structured generation with Outlines"
    Instead of writing complex parsing functions and hoping the LLM follows your format, you can use [Outlines](https://github.com/dottxt-ai/outlines) to **guarantee** structured output. Outlines constrains the LLM's generation to follow a specific schema, making parsing trivial:

    ```python
    import outlines
    from pydantic import BaseModel

    class Scores(BaseModel):
        creativity: int
        coherence: int
        grammar: int

    # Generate structured output directly
    model = outlines.from_openai(client, "gpt-4")
    generator = outlines.generate.json(model, Scores)
    scores = generator(prompt)  # Returns a Scores object, no parsing needed!
    ```

    With Outlines, you get type-safe, validated responses every time - eliminating the need for defensive parsing code.

## Step 2: Create the Judge Model

Now let's apply these principles to build a simple evaluation file:

```python title="eval_story_judge.py"
from dotevals import foreach, Result
from dotevals.evaluators import evaluator
from dotevals.metrics import accuracy
from types import SimpleNamespace

# Mock judge for testing - replace with your actual LLM
def get_mock_judge():
    """Create a mock judge that returns varied responses."""
    def generate(prompt):
        # Mock responses based on story content
        if "dragon" in prompt.lower():
            return "creativity: 8, coherence: 7, grammar: 9"
        elif "cat" in prompt.lower():
            return "creativity: 6, coherence: 9, grammar: 8"
        else:
            return "creativity: 5, coherence: 6, grammar: 7"

    return SimpleNamespace(generate=generate)

# Get the judge model once
judge_model = get_mock_judge()

# For real usage:
# from openai import OpenAI
# client = OpenAI(api_key="your-key")
# judge_model = client
```

## Step 3: Build the Evaluator

Create your custom evaluator using a closure to capture the model:

```python
def create_story_judge(judge_model):
    """Create a story judge evaluator with the model captured by closure."""

    @evaluator(metrics=accuracy())
    def story_judge(story: str) -> bool:
        """Judge story quality using an LLM."""
        prompt = f"""
You are evaluating a creative writing story. Rate each aspect from 1-10:

Story:
{story}

Provide ratings in this exact format:
creativity: [score], coherence: [score], grammar: [score]

Example: creativity: 8, coherence: 7, grammar: 9
"""
        # Use the model from closure - not passed as a parameter
        response = judge_model.generate(prompt)

        # Parse the response
        scores = {}
        for part in response.split(","):
            if ":" in part:
                criterion, score = part.split(":")
                criterion = criterion.strip()
                try:
                    scores[criterion] = int(score.strip())
                except ValueError:
                    scores[criterion] = 0

        # Return whether all scores are above threshold
        threshold = 7
        return all(score >= threshold for score in scores.values())

    return story_judge

# Create the evaluator once with the model
story_judge = create_story_judge(judge_model)
```

!!! info "Understanding the @evaluator decorator"
    The `@evaluator` decorator transforms your function into an evaluator that:
    - Tracks metrics across your dataset
    - Stores evaluation results and metadata
    - Integrates with dotevals's reporting system

    **Important:** Only pass serializable data (strings, numbers, booleans, lists, dicts) to evaluators. Non-serializable objects like model instances should be captured via closures instead.


## Step 4: Test Your Evaluator

Create test stories:

```python
stories = [
    "Once upon a time, a magical dragon discovered it could code in Python. It used its newfound skills to debug the kingdom's software problems.",
    "The cat sat on the mat. It was a normal day. The cat was happy.",
    "In a world where gravity worked backwards, Maria learned to walk on clouds and swim through air to reach her floating school.",
]

@foreach("story", stories)
def eval_creative_writing(story):
    """Evaluate creative writing using LLM judge."""
    return Result(
        story_judge(story),  # Use the evaluator created earlier
        prompt=story[:50] + "..."
    )
```

## Step 5: Run and Test

Run your evaluation:

```bash
pytest eval_story_judge.py --experiment story_quality
```

View the results:

```bash
dotevals show story_quality
```

You should see scores for each story showing the creativity, coherence, and grammar ratings.

## Step 6: Improve the Prompt

Let's make the judging more reliable with clearer criteria:

```python
def create_improved_story_judge(judge_model):
    """Create an improved story judge with clearer criteria."""

    @evaluator(metrics=accuracy())
    def improved_story_judge(story: str) -> bool:
        """Improved story judge with clearer criteria."""
        prompt = f"""
Evaluate this creative writing story on three criteria (1-10 scale):

CREATIVITY (1=cliché, 10=highly original):
- Unique ideas, unexpected elements, imaginative concepts

COHERENCE (1=confusing, 10=perfectly logical):
- Story makes sense, events connect logically, clear narrative

GRAMMAR (1=many errors, 10=perfect):
- Proper spelling, punctuation, sentence structure

Story to evaluate:
{story}

Respond with ONLY these three lines:
creativity: [number]
coherence: [number]
grammar: [number]
"""
        # Use the model from closure
        response = judge_model.generate(prompt)

        # More robust parsing
        scores = {}
        for line in response.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                try:
                    scores[key.strip()] = int(value.strip())
                except ValueError:
                    scores[key.strip()] = 0

        # Return whether story meets quality threshold
        threshold = 7
        return all(score >= threshold for score in scores.values())

    return improved_story_judge

# Create the improved evaluator
improved_story_judge = create_improved_story_judge(judge_model)
```


## Step 7: Test Multiple Stories

Create a more comprehensive test:

```python
story_dataset = [
    "The time-traveling librarian accidentally returned the wrong century's books, causing Shakespeare to write science fiction.",
    "I went to store. Bought milk. Came home.",
    "As the last star died, the cosmic janitor swept up the universe's debris, humming an ancient tune that would birth new galaxies.",
    "There was a dog named Rex. Rex was good dog. Rex played fetch every day.",
]

@foreach("story", story_dataset)
def eval_story_quality_final(story):
    """Final story quality evaluation."""
    return Result(
        improved_story_judge(story),  # Use the improved evaluator
        prompt=story[:60] + "..." if len(story) > 60 else story
    )
```

Run the improved evaluation:

```bash
pytest eval_story_judge.py::eval_story_quality_final --experiment improved_stories
```

## What you've learned

You now understand:

1. **LLM judge design** - Creating prompts with clear criteria and output formats
2. **Closure pattern** - Using closures to capture non-serializable objects like model instances
3. **Response parsing** - Robustly extracting structured data from LLM outputs
4. **Threshold-based evaluation** - Converting multiple scores into pass/fail decisions
5. **Iterative improvement** - How to refine prompts for better reliability
6. **Edge case handling** - Dealing with unexpected LLM responses


## Next Steps

**[Tutorial 5: Scale with Async Evaluation](05-scale-with-async-evaluation.md)** - Make your evaluations run 10x faster with async and concurrency.

## See Also

- **[How to Create an Evaluator Plugin](../how-to/plugins/create-evaluator-plugin.md)** - Share your custom evaluators as reusable plugins
- **[Reference: Evaluators](../reference/evaluators.md)** - Complete API documentation for evaluators
- **[Tutorial 7: Comparing Multiple Models](07-comparing-multiple-models.md)** - Use custom evaluators to compare model performance
