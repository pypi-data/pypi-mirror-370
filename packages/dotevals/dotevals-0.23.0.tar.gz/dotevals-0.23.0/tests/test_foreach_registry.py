"""Tests for ForEach class registry integration."""

from unittest.mock import patch

import pytest

from dotevals.core import ForEach, foreach
from dotevals.datasets import Dataset, DatasetRegistry
from dotevals.evaluators import exact_match
from dotevals.models import Result


class MockDataset(Dataset):
    """Simple test dataset."""

    name = "test_dataset"
    splits = ["train", "test"]
    columns = ["question", "answer"]

    def __init__(self, split, **kwargs):
        self.split = split
        self.limit = kwargs.get("limit", 2)
        self.num_rows = min(self.limit, 2)

    def __iter__(self):
        data = [("What is 2+2?", "4"), ("What is 3+3?", "6")]

        yield from data[: self.limit]


@pytest.fixture
def test_registry():
    """Provide clean registry with test data."""
    registry = DatasetRegistry()
    registry.register(MockDataset)
    return registry


def test_foreach_getattr_creates_decorator(test_registry):
    """Test that foreach.dataset_name() returns a decorator."""
    with patch("dotevals.core._registry", test_registry):
        decorator = foreach.test_dataset("test")
        assert callable(decorator)


def test_foreach_getattr_decorates_function(test_registry):
    """Test decorator properly wraps functions."""
    with patch("dotevals.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        def eval_fn(question, answer):
            return True

        assert callable(eval_fn)
        assert hasattr(eval_fn, "__wrapped__")


@pytest.mark.parametrize(
    "split,kwargs",
    [
        ("test", {}),
        ("train", {"limit": 1}),
    ],
)
def test_foreach_getattr_with_parameters(test_registry, split, kwargs):
    """Test foreach.dataset_name with different parameters."""
    with patch("dotevals.core._registry", test_registry):
        decorator = foreach.test_dataset(split, **kwargs)

        @decorator
        def eval_fn(question, answer):
            return True

        assert callable(eval_fn)


def test_foreach_getattr_preserves_function_metadata(test_registry):
    """Test decorator preserves function name and docstring."""
    with patch("dotevals.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        def my_evaluation(question, answer):
            """My test evaluation."""
            return True

        assert my_evaluation.__name__ == "my_evaluation"
        assert my_evaluation.__doc__ == "My test evaluation."


def test_foreach_getattr_nonexistent_dataset():
    """Test foreach.nonexistent raises appropriate error."""
    with pytest.raises(ValueError, match="Dataset 'nonexistent' not found"):
        foreach.nonexistent("test")


def test_foreach_getattr_async_function(test_registry):
    """Test foreach works with async functions."""
    with patch("dotevals.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        async def async_eval(question, answer):
            return True

        import asyncio

        assert asyncio.iscoroutinefunction(async_eval.__wrapped__)


def test_foreach_different_instances(test_registry):
    """Test ForEach instances behave consistently."""
    custom_foreach = ForEach()

    # Use mock dataset instead of real GSM8K
    with patch("dotevals.core._registry", test_registry):
        # Both should access same global registry
        decorator1 = foreach.test_dataset("test")
        decorator2 = custom_foreach.test_dataset("test")

        assert callable(decorator1)
        assert callable(decorator2)


def test_foreach_with_mock_dataset(test_registry):
    """Test foreach works with mock registered dataset."""
    # Use mock dataset instead of real GSM8K
    with patch("dotevals.core._registry", test_registry):
        decorator = foreach.test_dataset("test")

        @decorator
        def eval_mock(question, answer):
            return {"exact_match": True}

        assert callable(eval_mock)
        assert hasattr(eval_mock, "__wrapped__")


def test_foreach_getattr_without_split_argument():
    """Test foreach.dataset_name() works when split is omitted (split=None)."""

    class NoSplitDataset(Dataset):
        name = "no_split_dataset"
        splits = []
        columns = ["x", "y"]

        def __init__(self, **kwargs):
            self.num_rows = 1

        def __iter__(self):
            yield (1, 2)

    registry = DatasetRegistry()
    registry.register(NoSplitDataset)

    with patch("dotevals.core._registry", registry):
        decorator = foreach.no_split_dataset()

        @decorator
        def eval_fn(x, y):
            return Result(exact_match(x, y), prompt="")

        # Should be callable (actual execution would need session context)
        assert callable(eval_fn)
        # Verify it's set up for pytest integration
        assert hasattr(eval_fn, "__wrapped__")
