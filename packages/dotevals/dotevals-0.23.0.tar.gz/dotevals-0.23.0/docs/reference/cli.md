# Command Line Interface

The dotevals CLI provides powerful tools for managing evaluation sessions, viewing results, and monitoring progress.

## Installation

The CLI is included when you install dotevals:

```bash
pip install dotevals
```

Verify installation:

```bash
dotevals --help
```

## Core Commands

### `dotevals list`

List all available evaluation sessions.

```bash
dotevals list
```

**Options:**

- `--name TEXT` - Filter experiments by name (partial match)
- `--storage TEXT` - Storage backend path (default: `json://.dotevals`)

**Examples:**

```bash
# List all sessions
dotevals list

# Filter by name
dotevals list --name "gsm8k"

# Use custom storage location
dotevals list --storage "json://my_evals"
```

**Sample Output:**

```
Named Experiments
┌─────────────────────┬─────────────┐
│ Experiment Name     │ Evaluations │
├─────────────────────┼─────────────┤
│ gsm8k_baseline      │ 1           │
│ gsm8k_improved      │ 2           │
│ gpqa_evaluation     │ 1           │
└─────────────────────┴─────────────┘

Ephemeral Experiments
┌─────────────────────┬─────────────┐
│ Timestamp           │ Evaluations │
├─────────────────────┼─────────────┤
│ 20240115_143022_abc │ 1           │
│ 20240114_091533_def │ 1           │
└─────────────────────┴─────────────┘
```

### `dotevals show`

Display detailed information about a specific experiment.

```bash
dotevals show EXPERIMENT_NAME
```

**Options:**

- `--storage TEXT` - Storage backend path (default: `json://.dotevals`)
- `--evaluation TEXT` - Show specific evaluation results
- `--full` - Show complete session data in JSON format
- `--errors` - Show detailed error information

**Examples:**

```bash
# Show session summary
dotevals show gsm8k_baseline

# Show full session details
dotevals show gsm8k_baseline --full

# Show session from custom storage
dotevals show my_eval --storage "json://custom_path"
```

**Sample Output (Summary):**

```
Summary of gsm8k_baseline :: eval_gsm8k
┌────────────┬──────────┬───────┬────────┐
│ Evaluator  │ Metric   │ Score │ Errors │
├────────────┼──────────┼───────┼────────┤
│ exact_match│ accuracy │  0.73 │ 0/100  │
└────────────┴──────────┴───────┴────────┘
```

**Sample Output (Full):**

```json
{
  "name": "gsm8k_baseline",
  "status": "Completed",
  "created_at": 1705325422.123,
  "results": {
    "eval_gsm8k": [
      {
        "scores": [
          {
            "name": "exact_match",
            "value": true,
            "metrics": ["accuracy"],
            "metadata": {"value": "42", "expected": "42"}
          }
        ],
        "item_id": 0,
        "input_data": {"question": "What is 6*7?", "answer": "42"}
      }
    ]
  }
}
```

### `dotevals rename`

Rename an existing experiment.

```bash
dotevals rename OLD_NAME NEW_NAME
```

**Options:**

- `--storage TEXT` - Storage backend path (default: `json://.dotevals`)

**Examples:**

```bash
# Rename a session
dotevals rename old_experiment new_experiment

# Rename with custom storage
dotevals rename exp1 experiment_v2 --storage "json://my_evals"
```

### `dotevals delete`

Delete an experiment permanently.

```bash
dotevals delete EXPERIMENT_NAME
```

**Options:**

- `--storage TEXT` - Storage backend path (default: `json://.dotevals`)

**Examples:**

```bash
# Delete a session
dotevals delete failed_experiment

# Delete from custom storage
dotevals delete old_eval --storage "json://archived_evals"
```

!!! warning "Permanent Deletion"
    This action cannot be undone. All evaluation results for the experiment will be permanently lost.

### `dotevals datasets`

List available datasets that can be used with the `@foreach` decorator.

```bash
dotevals datasets
```

**Options:**

- `--verbose`, `-v` - Show detailed information for each dataset
- `--name TEXT`, `-n TEXT` - Filter datasets by name (case-insensitive partial match)

**Examples:**

```bash
# List all available datasets
dotevals datasets

# Show detailed information for each dataset
dotevals datasets --verbose

# Filter datasets by name
dotevals datasets --name gsm

# Combine options
dotevals datasets -v -n bfcl
```

**Sample Output (Summary):**

```
Available Datasets
┌─────────┬────────────────┬───────────────────────────────────┬──────────┐
│ Dataset │ Splits         │ Columns                           │     Rows │
├─────────┼────────────────┼───────────────────────────────────┼──────────┤
│ bfcl    │ simple,        │ question, schema, answer          │ streaming│
│         │ multiple,      │                                   │          │
│         │ parallel       │                                   │          │
│ gsm8k   │ train, test    │ question, reasoning, answer       │    8,792 │
│ sroie   │ train, test    │ images, address, company, date,   │    1,000 │
│         │                │ total                             │          │
└─────────┴────────────────┴───────────────────────────────────┴──────────┘

Use --verbose for detailed information and usage examples
```

**Sample Output (Verbose):**

```
╭─────────────────────────────────────────────────────────────────────╮
│ Dataset: gsm8k                                                      │
├────────────┬────────────────────────────────────────────────────────┤
│ Property   │ Value                                                  │
├────────────┼────────────────────────────────────────────────────────┤
│ Name       │ gsm8k                                                  │
│ Splits     │ train, test                                            │
│ Columns    │ question, reasoning, answer                            │
│ Rows       │ 8,792                                                  │
╰────────────┴────────────────────────────────────────────────────────╯

Usage:
  @foreach("question,reasoning,answer", gsm8k_test)
  def eval_gsm8k(question, reasoning, answer, model):
      # Your evaluation logic here
      pass
```

!!! info "Dataset Plugins"
    If no datasets are found, you need to install a dataset plugin:
    ```bash
    pip install dotevals-datasets
    ```

    You can also create custom dataset plugins. See [How to Create a Dataset Plugin](../how-to/plugins/create-dataset-plugin.md).

## Storage Backends

dotevals supports different storage backends for evaluation data:

### JSON Storage (Default)

```bash
# Default location
dotevals list --storage "json://.dotevals"

# Custom directory
dotevals list --storage "json://my_custom_path"

# Absolute path
dotevals list --storage "json:///home/user/evaluations"
```

The JSON storage backend stores each session as a separate JSON file in the specified directory.

### Plugin Storage Backends

Additional storage backends are available as plugins. For example, SQLite storage:

```bash
# Install SQLite storage plugin
pip install dotevals-storage-sqlite

# Use SQLite storage
dotevals list --storage "sqlite://results.db"
pytest eval.py --storage "sqlite://evaluations.db" --experiment my_eval
```

For more storage options, see [Storage Backends](storage.md).

## Usage Examples

```bash
# Run evaluation with experiment name
pytest eval_model.py --experiment "model_baseline"

# Check results
dotevals show "model_baseline"

# Run batch evaluations
for dataset in gsm8k gpqa; do
    pytest "eval_${dataset}.py" --experiment "${dataset}_eval"
done

# Development testing with limited samples
pytest eval_test.py --experiment dev_test --samples 10
```

## Troubleshooting

### Common Issues

#### Session Not Found
```bash
dotevals show my_session
# Error: Session 'my_session' not found
```
**Solution**: Check available sessions with `dotevals list` and verify the session name.

#### Storage Access Error
```bash
dotevals list --storage "json://restricted_path"
# Error: Permission denied
```
**Solution**: Ensure you have read/write permissions to the storage directory.

#### Interrupted Session
```bash
dotevals list
# Shows session as "Interrupted"
```
**Solution**: Resume by running the original pytest command again.

### Getting Help

```bash
# General help
dotevals --help

# Command-specific help
dotevals list --help
dotevals show --help
dotevals rename --help
dotevals delete --help
dotevals datasets --help
```

## See Also

### Core Concepts
- **[Experiments](experiments.md)** - Understand the experiment lifecycle that CLI commands manage
- **[Storage Backends](storage.md)** - Learn about storage configuration options available via CLI

### Integration Guides
- **[Pytest Integration](pytest.md)** - See how CLI options integrate with pytest-based evaluation execution
- **[@foreach Decorator](foreach.md)** - Understand how CLI parameters affect `@foreach` evaluation behavior
- **[Async Evaluations](async.md)** - Control async evaluation execution with CLI concurrency options

### Advanced Usage
- **[Evaluators](evaluators.md)** - View evaluator results through CLI display tools
- **[Metrics](metrics.md)** - Access computed metrics via CLI session viewing commands

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with basic CLI usage for running evaluations
- **[Build a Production Evaluation Pipeline](../tutorials/08-build-production-evaluation-pipeline.md)** - Master CLI workflow patterns for production systems
- **[Comparing Multiple Models](../tutorials/07-comparing-multiple-models.md)** - Use CLI commands to organize and compare evaluation results
