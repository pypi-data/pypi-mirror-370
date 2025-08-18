"""Integration tests for fixture handling with foreach decorator."""

import tempfile
from pathlib import Path

import pytest

from dotevals import foreach
from dotevals.evaluators import exact_match
from dotevals.models import Result


# Test fixture that will be used with indirect parametrization
@pytest.fixture
def application(request):
    """Fixture that processes application configuration from parametrized values."""
    model_name = request.param

    # Simulate different model configurations
    if model_name == "model_a":
        model = lambda prompt: "result_a"
        template = lambda **kwargs: f"Model A: {kwargs.get('question', '')}"
        output_structure = {"type": "model_a"}
    elif model_name == "model_b":
        model = lambda prompt: "result_b"
        template = lambda **kwargs: f"Model B: {kwargs.get('question', '')}"
        output_structure = {"type": "model_b"}
    else:
        model = lambda prompt: "result_c"
        template = lambda **kwargs: f"Model C: {kwargs.get('question', '')}"
        output_structure = {"type": "model_c"}

    return model, template, output_structure


# Test with foreach decorator directly on the test function
@pytest.mark.parametrize(
    "application",
    ["model_a", "model_b", "model_c"],
    indirect=True,
)
@foreach("question,answer", [("What is 2+2?", "4"), ("What is 3+3?", "6")])
def test_foreach_with_indirect_parametrization(question, answer, application):
    """Test that foreach decorator works with indirect parametrization."""
    model, template, output_structure = application
    prompt = template(question=question)

    # Simulate model processing
    result = model(prompt)

    # For testing, just check if we got a result
    score = (
        exact_match(result, "result_a")
        if output_structure["type"] == "model_a"
        else exact_match(result, result)
    )

    return Result(score, prompt=prompt)


# Test async version
@pytest.mark.parametrize(
    "application",
    ["model_a", "model_b"],
    indirect=True,
)
@foreach("question,answer", [("Async question?", "Async answer")])
async def test_async_foreach_with_indirect_parametrization(
    question, answer, application
):
    """Test that async foreach decorator works with indirect parametrization."""
    model, template, output_structure = application
    prompt = template(question=question)

    # Simulate async model processing
    import asyncio

    await asyncio.sleep(0.01)
    result = model(prompt)

    # For testing, just check if we got a result
    score = (
        exact_match(result, "result_a")
        if output_structure["type"] == "model_a"
        else exact_match(result, result)
    )

    return Result(score, prompt=prompt)


# Test with multiple fixtures
@pytest.fixture
def additional_config():
    """Another fixture to test multiple fixture resolution."""
    return {"extra": "config"}


@pytest.mark.parametrize(
    "application",
    ["model_a"],
    indirect=True,
)
@foreach("question,answer", [("Multi fixture test?", "42")])
def test_foreach_with_multiple_fixtures(
    question, answer, application, additional_config
):
    """Test that foreach works with multiple fixtures including indirect ones."""
    model, template, output_structure = application
    prompt = template(question=question)

    # Use both fixtures
    result = model(prompt)
    extra = additional_config.get("extra", "")

    score = (
        exact_match(result, "result_a")
        if output_structure["type"] == "model_a"
        else exact_match(result, result)
    )

    return Result(score, prompt=f"{prompt} [{extra}]")


# Tests documenting the limitation with fixture teardown in deferred execution


class ResourceTracker:
    """Helper class to track resource lifecycle."""

    def __init__(self):
        self.created = False
        self.destroyed = False
        self.file_path = None


# Global tracker to verify teardown behavior
tracker = ResourceTracker()


@pytest.fixture
def resource_with_teardown():
    """Fixture that creates and cleans up a resource.

    This fixture demonstrates the teardown limitation: the teardown
    happens before evaluations run in the deferred execution model.
    """
    # Setup: Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test data")
        tracker.file_path = Path(f.name)
        tracker.created = True
        yield f.name

    # Teardown: Remove the file
    if tracker.file_path and tracker.file_path.exists():
        tracker.file_path.unlink()
    tracker.destroyed = True


# Test dataset
teardown_dataset = [("item1",), ("item2",)]


@foreach("item", teardown_dataset)
def eval_fixture_teardown_now_works(item, resource_with_teardown):
    """Evaluation that demonstrates fixture teardown now works correctly.

    The fixture's teardown (file deletion) now happens after the evaluation
    completes, thanks to our deferred fixture management.
    """
    # The file should exist during evaluation
    assert Path(resource_with_teardown).exists(), (
        f"File {resource_with_teardown} should exist during evaluation. "
        f"Tracker shows: created={tracker.created}, destroyed={tracker.destroyed}"
    )
    return Result(prompt=f"Processed {item} with {resource_with_teardown}")


@pytest.fixture
def simple_config():
    """Simple fixture without teardown - this works fine."""
    return {"model": "test-model", "temperature": 0.7}


@foreach("prompt", [("test1",), ("test2",)])
def eval_fixture_without_teardown_works(prompt, simple_config):
    """Evaluation showing that fixtures without teardown work correctly."""
    assert simple_config["model"] == "test-model"
    return Result(prompt=f"{prompt} with {simple_config['model']}")


# Note: The runner setup/teardown pattern has been replaced by ModelProvider
# See the ModelProvider documentation for managing resources with proper lifecycle
