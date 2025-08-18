# Installation

## Requirements

Python 3.10 or higher. Check your version:

```bash
python --version
```

## Install dotevals

```bash
pip install dotevals
```

## Install Plugins (Optional)

dotevals uses a plugin system for extended functionality:

```bash
# For standard benchmark datasets (GSM8K, MMLU, HumanEval)
pip install dotevals-datasets

# For LLM-based evaluators (judges, semantic similarity)
pip install dotevals-evaluators-llm

# For SQLite storage with advanced querying
pip install dotevals-storage-sqlite

# For distributed execution on Modal
pip install dotevals-modal
```

See [Available Plugins](reference/plugins.md) for the complete list.

## Verify Installation

```bash
# Check import and version
python -c "import dotevals; print(f'✓ dotevals {dotevals.__version__}')"

# Check CLI
dotevals --help
```

## Quick Test

Create `test_install.py`:

```python
from dotevals import foreach
from dotevals.evaluators import exact_match

@foreach("q,a", [("2+2?", "4")])
def test_eval(q, a):
    return exact_match("4", a)
```

Run it:

```bash
pytest test_install.py
```

## Development Installation

For contributors:

```bash
git clone https://github.com/dottxt-ai/dotevals.git
cd dotevals
pip install -e ".[test,docs]"
```

## Next Steps

- **[Quickstart](quickstart.md)** - Your first evaluation in 30 seconds
- **[Tutorial](tutorials/01-your-first-evaluation.md)** - Step-by-step guide
