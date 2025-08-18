# Tutorial 6: Share Expensive Resources

In this tutorial, you'll learn to efficiently manage expensive model instances and API connections using pytest fixtures.

## What you'll learn

- How to create and share expensive model instances
- How to pool API connections efficiently

## Step 1: Basic Fixture Usage

Pytest fixtures help you set up expensive resources once and reuse them across your evaluation:

```python title="eval_basic_fixtures.py"
import time
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

@pytest.fixture
def sentiment_model():
    """Create an expensive model instance once per evaluation."""
    print("🔄 Loading sentiment model...")

    class SentimentModel:
        def __init__(self):
            time.sleep(2)  # Simulate expensive model loading
            self.load_time = time.time()
            self.call_count = 0

        def classify(self, text):
            self.call_count += 1
            return "positive" if "good" in text.lower() else "negative"

        def get_stats(self):
            return f"Model used {self.call_count} times"

    model = SentimentModel()
    yield model
    print(f"🗑️  Model cleanup: {model.get_stats()}")

# Test data - 3 data points will share the same model instance
test_data = [
    ("This is good", "positive"),
    ("This is bad", "negative"),
    ("Really good stuff", "positive"),
]

@foreach("text,expected", test_data)
def eval_sentiment(text, expected, sentiment_model):
    """All data points share the same model instance."""
    prediction = sentiment_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

Run the evaluation:

```bash
pytest eval_basic_fixtures.py::eval_sentiment --experiment sentiment_test -v
```

You'll see the model is created once and used 3 times (once per data point).

!!! info "How Fixtures Work in dotevals"

    **Key insight**: Fixtures are created **once per evaluation function**, not per data point.

    - An evaluation with 100 data points still creates the fixture only once
    - All data points in that evaluation share the same fixture instance
    - This makes fixtures perfect for expensive model loading and API connections

## Step 2: Sharing Fixtures Between Evaluations

When you have multiple evaluation functions, each gets its own fixture instance by default. If you want to share expensive resources across multiple evaluations, use session scope:

```python title="eval_shared_fixtures.py"
import time
import pytest
from dotevals import foreach, Result
from dotevals.evaluators import exact_match

@pytest.fixture(scope="session")
def shared_model():
    """Shared model across all evaluations in this session."""
    print("🚀 Creating shared model (once for entire session)...")

    class SharedModel:
        def __init__(self):
            time.sleep(2)  # Expensive setup
            self.call_count = 0

        def classify(self, text):
            self.call_count += 1
            return "positive" if "good" in text.lower() else "negative"

        def get_stats(self):
            return f"Model used {self.call_count} times total"

    model = SharedModel()
    yield model
    print(f"🗑️  Session cleanup: {model.get_stats()}")

# Test data
data_set_1 = [("good", "positive"), ("bad", "negative")]
data_set_2 = [("really good", "positive"), ("very bad", "negative")]

@foreach("text,expected", data_set_1)
def eval_dataset_1(text, expected, shared_model):
    """First evaluation using shared model."""
    prediction = shared_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)

@foreach("text,expected", data_set_2)
def eval_dataset_2(text, expected, shared_model):
    """Second evaluation using same shared model."""
    prediction = shared_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

Run both evaluations:

```bash
pytest eval_shared_fixtures.py --experiment shared_models -v -s
```

You'll see the model is created once and used by both evaluations (4 times total).

## When to Use Fixtures

Fixtures are perfect for expensive operations that you don't want to repeat. Here are the most common use cases:

### 🤖 Local Model Loading

Load heavy models:

```python
@pytest.fixture
def embedding_model():
    """Load sentence transformer once per evaluation."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')  # ~90MB download
    print("🗑️ Unloading embedding model")

@foreach("text,expected_embedding", embedding_data)
def eval_embeddings(text, expected_embedding, embedding_model):
    # Model is loaded once, used for all data points
    embedding = embedding_model.encode(text)
    return Result(cosine_similarity(embedding, expected_embedding))
```

### 🌐 API Connection Pooling

Create persistent connections to avoid authentication overhead:

```python
@pytest.fixture
def openai_client():
    """Reuse OpenAI client connection."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    yield client

@foreach("prompt,expected", llm_test_data)
def eval_llm_responses(prompt, expected, openai_client):
    # Reuses authenticated connection for all requests
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return Result(exact_match(response.choices[0].message.content, expected))
```

### 🗄️ Database Connections

Set up database connections and test data once:

```python
@pytest.fixture
def test_database():
    """Set up test database with sample data."""
    import sqlite3

    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create schema and insert test data
    cursor.execute('''
        CREATE TABLE evaluations (id INTEGER, result TEXT, score REAL)
    ''')
    cursor.execute("INSERT INTO evaluations VALUES (1, 'positive', 0.85)")
    cursor.execute("INSERT INTO evaluations VALUES (2, 'negative', 0.12)")

    yield conn
    conn.close()
```


### When NOT to Use Fixtures

Don't use fixtures for:

- **Simple values** - Just use function parameters
- **Fast operations** - No need to optimize quick operations
- **Test-specific data** - Data that changes per test should be in the test

## What you've learned

You now understand:

1. **Fixture basics** - How to create expensive resources once per evaluation
2. **Fixture scoping** - When to use function vs session scope for resource sharing
3. **Common use cases** - Model loading, API connections, databases, and caching
4. **When to avoid fixtures** - Simple values and fast operations don't need fixtures

## Next Steps

**[Tutorial 7: Comparing Multiple Models](07-comparing-multiple-models.md)** - Use fixtures with parametrized model comparisons to test multiple models efficiently.
