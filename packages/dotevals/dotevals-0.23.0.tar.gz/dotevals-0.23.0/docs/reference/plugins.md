# Available Plugins

This reference lists all official and community dotevals plugins. For creating your own plugins, see the [How-To Guides](../how-to/index.md). For understanding the plugin architecture, see [Plugin Architecture](../explanation/plugin-architecture.md).

## Plugin Types

| Type | Purpose | Entry Point |
|------|---------|-------------|
| **Model Providers** | Manage LLM lifecycle and connections | `dotevals.model_providers` |
| **Evaluators** | Define evaluation logic | Direct import |
| **Storage Backends** | Persist evaluation results | `dotevals.storage` |
| **Runners** | Execute evaluations in different environments | `dotevals.runners` |
| **Datasets** | Provide evaluation datasets | `dotevals.datasets` |

## Official Plugins

### dotevals-modal
**Type**: Model Provider & Runner
**Install**: `pip install dotevals-modal`
**Purpose**: Deploy vLLM servers on Modal's GPU infrastructure

**Features**:

- Automatic vLLM server deployment
- Server pooling for cost optimization
- GPU cost tracking
- Support for any HuggingFace model

**Usage**:
```bash
pytest eval.py --runner modal --modal-model meta-llama/Llama-3-8b
```

**Configuration Options**:

- `--modal-gpu-type`: GPU type (a10g, a100, h100, l4, t4)
- `--modal-max-servers`: Maximum concurrent servers
- `--modal-idle-timeout`: Server idle timeout in seconds

---

### dotevals-vllm
**Type**: Model Provider
**Install**: `pip install dotevals-vllm`
**Purpose**: Local vLLM integration for self-hosted models

**Features**:

- Local GPU utilization
- Batch inference support
- Custom model loading

**Fixture**: `vllm_client`

---

### dotevals-sagemaker
**Type**: Model Provider & Runner
**Install**: `pip install dotevals-sagemaker`
**Purpose**: AWS SageMaker integration

**Features**:

- SageMaker endpoint management
- Auto-scaling support
- AWS cost tracking

---

### dotevals-evaluators-llm
**Type**: Evaluators
**Install**: `pip install dotevals-evaluators-llm`
**Purpose**: LLM-based evaluation methods

**Evaluators**:

- `llm_judge`: LLM-based evaluation with custom criteria
- `semantic_similarity`: Embedding-based similarity scoring
- `factual_consistency`: Fact-checking against references
- `answer_relevance`: Relevance scoring
- `response_quality`: Multi-dimensional quality assessment

**Example**:
```python
from dotevals.evaluators import llm_judge

score = await llm_judge(
    response,
    expected,
    judge_model=judge,
    criteria="Is the response helpful and accurate?"
)
```

---

### dotevals-storage-sqlite
**Type**: Storage Backend
**Install**: `pip install dotevals-storage-sqlite`
**Purpose**: SQLite storage with advanced querying

**Features**:

- SQL query capabilities
- Transaction support
- Concurrent access handling
- Efficient batch operations

**Usage**:
```bash
pytest eval.py --storage sqlite://results.db
dotevals show experiment --storage sqlite://results.db
```

---

### dotevals-datasets
**Type**: Datasets
**Install**: `pip install dotevals-datasets`
**Purpose**: Standard benchmark datasets

**Available Datasets**:

- `gsm8k`: Grade school math problems
- `mmlu`: Massive Multitask Language Understanding
- `humaneval`: Python programming problems
- `bfcl`: Berkeley Function Calling Leaderboard
- `gpqa`: Graduate-level Q&A

**Usage**:
```python
@foreach.gsm8k("test")
def eval_math(question, reasoning, answer, model):
    response = model.solve(question)
    return numeric_match(response, answer)
```

## Community Plugins

*To add your plugin here, submit a PR to the documentation.*

## Installing Plugins

### Individual Installation
```bash
pip install dotevals-modal
pip install dotevals-storage-sqlite
```

### Multiple Plugins
```bash
pip install dotevals dotevals-modal dotevals-storage-sqlite dotevals-evaluators-llm
```

### Development Installation
```bash
git clone https://github.com/your-org/dotevals-yourplugin
cd dotevals-yourplugin
pip install -e .
```

## Using Plugins

### Model Providers
Model providers are accessed through pytest fixtures:

```python
@pytest.fixture
def model():
    # Your model provider
    return load_model()

@foreach("prompt,expected", dataset)
async def eval_with_model(prompt, expected, model):
    response = await model.generate(prompt)
    return exact_match(response, expected)
```

### Storage Backends
Storage backends are selected via URL scheme:

```bash
# JSON (default)
--storage json://.dotevals

# SQLite
--storage sqlite://results.db

# Custom backend
--storage mybackend://config
```

### Runners
Runners are selected via CLI option:

```bash
# Local (default)
pytest eval.py

# Modal
pytest eval.py --runner modal

# Custom runner
pytest eval.py --runner myrunner
```

### Datasets
Datasets are accessed through the `foreach` decorator:

```python
# Using dataset fixtures
@foreach.gsm8k("test")
def eval_math(question, answer, model):
    # ...

# Custom parameters
@foreach.mmlu(subject="mathematics", split="test")
def eval_mmlu(question, choices, answer, model):
    # ...
```

## Plugin Discovery

Plugins are discovered through Python entry points defined in `pyproject.toml`:

```toml
[project.entry-points."dotevals.model_providers"]
myprovider = "my_plugin:provider_fixture"

[project.entry-points."dotevals.storage"]
mybackend = "my_plugin:MyStorage"

[project.entry-points."dotevals.runners"]
myrunner = "my_plugin:MyRunner"

[project.entry-points.pytest11]
my_plugin = "my_plugin.pytest_plugin"
```

## Troubleshooting

### Plugin Not Found
- Verify installation: `pip list | grep dotevals`
- Check entry points are registered correctly
- Ensure plugin is installed in same environment

### Storage Backend Not Recognized
- Check URL scheme matches registered backend
- Verify storage plugin is installed
- List available backends: `python -c "from dotevals.storage import list_backends; print(list_backends())"`

### Model Provider Fixture Not Available
- Ensure model provider plugin is installed
- Check pytest can discover the fixture: `pytest --fixtures | grep provider_name`

## See Also

- [Plugin Architecture](../explanation/plugin-architecture.md) - Understanding how plugins work
- [Creating Model Provider Plugins](../how-to/plugins/create-model-provider-plugin.md)
- [Creating Storage Plugins](../how-to/plugins/create-storage-plugin.md)
- [Creating Evaluator Plugins](../how-to/plugins/create-evaluator-plugin.md)
- [Creating Dataset Plugins](../how-to/plugins/create-dataset-plugin.md)
