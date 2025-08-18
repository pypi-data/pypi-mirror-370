# Tutorial 8: Build Production Evaluation Pipeline

In this tutorial, you'll create a complete evaluation pipeline that runs in CI/CD and tracks performance over time.

## What you'll learn

- How to build evaluations for complex multi-step workflows
- How to use SQLite storage for better performance and querying
- How to leverage automatic git tracking for reproducibility
- How to set up CI/CD automation for continuous evaluation

## Step 1: Create Agent Workflow Evaluation

Start by building an evaluation for complex agent scenarios:

```python title="eval_agent_workflows.py"
import json
import asyncio
from dotevals import foreach, Result
from dotevals.evaluators import exact_match


def load_agent_scenarios():
    """Load multi-step agent evaluation scenarios."""
    return [
        {
            "scenario": "Book a restaurant reservation",
            "initial_state": {"user_location": "San Francisco", "date": "tomorrow"},
            "expected_actions": [
                {"type": "search", "query": "restaurants near me"},
                {"type": "call", "restaurant": "Best Italian"},
                {"type": "book", "time": "7pm", "party_size": 2},
            ],
            "success_criteria": [
                "reservation_confirmed",
                "correct_time",
                "correct_party_size",
            ],
        }
    ]


class MockAgent:
    """Mock agent for demonstration - replace with your actual agent."""

    async def execute_scenario(self, scenario, initial_state):
        """Simulate agent executing a multi-step scenario."""
        await asyncio.sleep(0.1)  # Simulate processing time

        # Return mock response for restaurant reservation
        return [
            {"type": "search", "query": "restaurants near me", "results": 5},
            {"type": "call", "restaurant": "Best Italian", "status": "answered"},
            {"type": "book", "time": "7pm", "party_size": 2, "status": "confirmed"},
        ]


def evaluate_criterion(actions, criterion, expected_actions):
    """Evaluate specific success criteria for restaurant reservation."""
    if criterion == "reservation_confirmed":
        return any(
            action.get("type") == "book" and action.get("status") == "confirmed"
            for action in actions
        )
    elif criterion == "correct_time":
        booking_action = next((a for a in actions if a.get("type") == "book"), {})
        expected_time = next(
            (a.get("time") for a in expected_actions if a.get("type") == "book"), None
        )
        return booking_action.get("time") == expected_time
    elif criterion == "correct_party_size":
        booking_action = next((a for a in actions if a.get("type") == "book"), {})
        expected_size = next(
            (a.get("party_size") for a in expected_actions if a.get("type") == "book"),
            None,
        )
        return booking_action.get("party_size") == expected_size
    return False


@foreach(
    "scenario,initial_state,expected_actions,success_criteria", load_agent_scenarios()
)
async def eval_agent_workflow(
    scenario, initial_state, expected_actions, success_criteria
):
    """Evaluate an agent's ability to complete multi-step workflows."""
    agent = MockAgent()

    # Execute agent workflow
    actions = await agent.execute_scenario(scenario, initial_state)

    # Evaluate each success criterion
    scores = []
    for criterion in success_criteria:
        success = evaluate_criterion(actions, criterion, expected_actions)
        scores.append(exact_match(success, True, name=criterion))

    return Result(
        *scores,
        prompt=f"Scenario: {scenario}",
        model_response=json.dumps(actions, indent=2),
    )
```

Test your agent evaluation:

```bash
pytest eval_agent_workflows.py --experiment agent_test
```

## Step 2: Switch to SQLite Storage

For production pipelines, SQLite provides better performance and querying capabilities than JSON storage.

### Installing SQLite Support

Simply install the SQLite plugin:

```bash
pip install dotevals-sqlite
```

That's it! The plugin automatically registers itself with dotevals. No configuration needed.

!!! info "The Power of Plugins"
    Doteval's plugin architecture means everything beyond core evaluation is extensible - storage backends, evaluators, metrics, datasets, and model providers are all plugins. This design keeps the core lightweight while allowing you to add only what you need.

    The `dotevals-*` namespace contains official plugins that integrate seamlessly:

    - `dotevals-sqlite` - SQLite storage for production pipelines
    - `dotevals-datasets-common` - Common datasets used in evaluations
    - `dotevals-vllm` - Run evaluations using a local vLLM instance
    - `dotevals-modal-vllm` - Run evaluations on Modal's serverless infrastructure

    You can even create your own plugins to share evaluation tools with your team or the community.

### Using SQLite Storage

Once installed, you can use SQLite storage by specifying a `sqlite://` URL:

```bash
# Run evaluation with SQLite storage
pytest eval_agent_workflows.py --experiment agent_baseline --storage sqlite://agent_results.db
```

View the results:

```bash
# Query results from SQLite database
dotevals show agent_baseline --storage sqlite://agent_results.db
```

!!! tip "Storage Backend Selection"
    The `--storage` parameter tells dotevals where to look for results. Without it, dotevals defaults to `json://.dotevals`. Once you start using SQLite, you'll need to specify `--storage sqlite://your_database.db` when reading results.

## Step 4: Create CI/CD Integration

Set up automated evaluation in GitHub Actions:

```yaml title=".github/workflows/agent-evaluation.yml"
name: Agent Evaluation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  evaluate-agent:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install dotevals
        pip install dotevals-sqlite  # Enable SQLite storage
        # Add your other dependencies here

    - name: Run Agent Evaluation
      run: |
        pytest eval_agent_workflows.py \
          --experiment "agent_ci_${{ github.run_number }}" \
          --storage sqlite://agent_results.db

    - name: Upload Results Database
      uses: actions/upload-artifact@v4
      with:
        name: agent-evaluation-results
        path: agent_results.db

    - name: Display Evaluation Results
      run: |
        dotevals show "agent_ci_${{ github.run_number }}" \
          --storage sqlite://agent_results.db
```

For local development, create a simple script:

```bash title="run_evaluation.sh"
#!/bin/bash

# Generate unique experiment name with timestamp
EXPERIMENT_NAME="agent_dev_$(date +%Y%m%d_%H%M%S)"

echo "Running agent evaluation: $EXPERIMENT_NAME"

pytest eval_agent_workflows.py \
  --experiment "$EXPERIMENT_NAME" \
  --storage sqlite://agent_results.db

echo "Evaluation complete. View results with:"
echo "dotevals show $EXPERIMENT_NAME --storage sqlite://agent_results.db"
```

Make it executable and run:

```bash
chmod +x run_evaluation.sh
./run_evaluation.sh
```


## What you've learned

You now understand:

1. **Complex evaluations** - Building multi-step agent workflow evaluations
2. **SQLite integration** - Using database storage for better querying and CI/CD
3. **Git tracking** - Leveraging automatic git metadata for reproducibility
4. **CI/CD automation** - Setting up pipelines for continuous evaluation

## Conclusion

Congratulations! You now have a complete, production-ready evaluation pipeline that scales with your development workflow. You've learned to build complex evaluations, leverage SQLite for better performance, track changes with git integration, and set up CI/CD automation.
