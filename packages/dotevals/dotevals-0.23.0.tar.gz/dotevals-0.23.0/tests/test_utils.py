"""Tests for utility functions in dotevals.utils."""

import io
from unittest.mock import patch

import pytest
from PIL import Image

from dotevals.models import Record, Result, Score
from dotevals.utils import (
    deserialize_records,
    deserialize_value,
    recursive_map,
    serialize_records,
    serialize_value,
)


def test_recursive_map():
    """Test the recursive_map function with different transform functions."""
    test_data = {"a": "123", "b": 456, "c": ["789", 101]}

    # Test with int transform function
    result_int = recursive_map(test_data, int)
    assert result_int == {"a": 123, "b": 456, "c": [789, 101]}

    # Test with float transform function
    result_float = recursive_map(test_data, float)
    assert result_float == {"a": 123.0, "b": 456.0, "c": [789.0, 101.0]}

    # Test with str transform function
    result_str = recursive_map(test_data, str)
    assert result_str == {"a": "123", "b": "456", "c": ["789", "101"]}

    # Test with nested structures
    nested_data = {"dict": {"x": "1", "y": 2}, "list": ["3", 4], "set": {"5", 6}}
    result_nested = recursive_map(nested_data, int)
    assert result_nested == {"dict": {"x": 1, "y": 2}, "list": [3, 4], "set": {5, 6}}

    # Test with custom transform function
    def double_value(val):
        return val * 2 if isinstance(val, (int | float)) else val

    result_double = recursive_map(test_data, double_value)
    assert result_double == {"a": "123", "b": 912, "c": ["789", 202]}


def test_serialize_value_with_pil_image():
    """Test serialize_value with PIL Image."""
    # Create a simple PIL Image
    img = Image.new("RGB", (10, 10), color="red")

    serialized = serialize_value(img)

    assert isinstance(serialized, dict)
    assert serialized["__type__"] == "PIL.Image"
    assert "data" in serialized
    assert serialized["mode"] == "RGB"
    assert serialized["size"] == (10, 10)


def test_serialize_value_with_nested_structures():
    """Test serialize_value with nested data structures."""
    test_data = {
        "list": [1, 2, 3],
        "tuple": (4, 5, 6),
        "set": {7, 8, 9},
        "dict": {"a": 1, "b": 2},
    }

    serialized = serialize_value(test_data)

    assert serialized["list"] == [1, 2, 3]
    assert serialized["tuple"]["__type__"] == "tuple"
    assert serialized["tuple"]["data"] == [4, 5, 6]
    assert serialized["set"]["__type__"] == "set"
    assert set(serialized["set"]["data"]) == {7, 8, 9}
    assert serialized["dict"] == {"a": 1, "b": 2}


def test_deserialize_value_with_pil_image():
    """Test deserialize_value with PIL Image."""
    # Create a simple PIL Image and serialize it
    img = Image.new("RGB", (10, 10), color="red")
    serialized = serialize_value(img)

    deserialized = deserialize_value(serialized)

    assert isinstance(deserialized, Image.Image)
    assert deserialized.mode == "RGB"
    assert deserialized.size == (10, 10)


def test_deserialize_value_with_nested_structures():
    """Test deserialize_value with nested data structures."""
    test_data = {
        "list": [1, 2, 3],
        "tuple": (4, 5, 6),
        "set": {7, 8, 9},
        "dict": {"a": 1, "b": 2},
    }

    serialized = serialize_value(test_data)
    deserialized = deserialize_value(serialized)

    assert deserialized["list"] == [1, 2, 3]
    assert deserialized["tuple"] == (4, 5, 6)
    assert deserialized["set"] == {7, 8, 9}
    assert deserialized["dict"] == {"a": 1, "b": 2}


def test_serialize_records():
    """Test serialize_records function."""

    # Create a mock metric function
    def mock_metric(x):
        return x

    mock_metric.__name__ = "mock_metric"

    # Create test records
    score1 = Score(
        name="accuracy", value=0.8, metrics=[mock_metric], metadata={"key": "value"}
    )
    score2 = Score(name="precision", value=0.9, metrics=[mock_metric], metadata={})

    result = Result(
        score1, score2, prompt="test prompt", model_response="test response"
    )
    record = Record(
        result=result,
        item_id="test_id",
        dataset_row={"input": "test input"},
        error=None,
        timestamp=1234567890,
    )

    serialized = serialize_records([record])

    assert len(serialized) == 1
    assert serialized[0]["item_id"] == "test_id"
    assert serialized[0]["result"]["prompt"] == "test prompt"
    assert serialized[0]["result"]["model_response"] == "test response"
    assert len(serialized[0]["result"]["scores"]) == 2
    assert serialized[0]["result"]["scores"][0]["name"] == "accuracy"
    assert serialized[0]["result"]["scores"][0]["value"] == 0.8
    assert serialized[0]["result"]["scores"][0]["metrics"] == ["mock_metric"]
    assert serialized[0]["result"]["scores"][0]["metadata"] == {"key": "value"}
    assert serialized[0]["dataset_row"] == {"input": "test input"}
    assert serialized[0]["timestamp"] == 1234567890


def test_deserialize_records():
    """Test deserialize_records function."""

    # Create a mock metric function
    def mock_metric(x):
        return x

    mock_metric.__name__ = "mock_metric"

    # Mock the registry using patch
    import dotevals.metrics

    with patch.object(dotevals.metrics, "registry", {"mock_metric": mock_metric}):
        # Create test data
        test_data = [
            {
                "item_id": "test_id",
                "result": {
                    "prompt": "test prompt",
                    "scores": [
                        {
                            "name": "accuracy",
                            "value": 0.8,
                            "metrics": ["mock_metric"],
                            "metadata": {"key": "value"},
                        }
                    ],
                    "error": None,
                    "model_response": "test response",
                },
                "dataset_row": {"input": "test input"},
                "error": None,
                "timestamp": 1234567890,
            }
        ]

        deserialized = deserialize_records(test_data)

        assert len(deserialized) == 1
        assert deserialized[0].item_id == "test_id"
        assert deserialized[0].result.prompt == "test prompt"
        assert deserialized[0].result.model_response == "test response"
        assert len(deserialized[0].result.scores) == 1
        assert deserialized[0].result.scores[0].name == "accuracy"
        assert deserialized[0].result.scores[0].value == 0.8
        assert deserialized[0].result.scores[0].metrics == [mock_metric]
        assert deserialized[0].result.scores[0].metadata == {"key": "value"}
        assert deserialized[0].dataset_row == {"input": "test input"}
        assert deserialized[0].timestamp == 1234567890


def test_serialize_records_with_errors():
    """Test serialize_records with records that have errors."""

    # Create a mock metric function
    def mock_metric(x):
        return x

    mock_metric.__name__ = "mock_metric"

    # Create test records with errors
    score = Score(name="accuracy", value=0.8, metrics=[mock_metric], metadata={})
    result = Result(
        score, prompt="test prompt", error="test error", model_response="test response"
    )
    record = Record(
        result=result,
        item_id="test_id",
        dataset_row={"input": "test input"},
        error="record error",
        timestamp=None,
    )

    serialized = serialize_records([record])

    assert len(serialized) == 1
    assert serialized[0]["result"]["error"] == "test error"
    assert serialized[0]["error"] == "record error"
    assert serialized[0]["timestamp"] is None


def test_deserialize_records_with_errors():
    """Test deserialize_records with records that have errors and missing timestamps."""

    # Create a mock metric function
    def mock_metric(x):
        return x

    mock_metric.__name__ = "mock_metric"

    # Mock the registry using patch
    import dotevals.metrics

    with patch.object(dotevals.metrics, "registry", {"mock_metric": mock_metric}):
        # Create test data with errors and missing timestamp
        test_data = [
            {
                "item_id": "test_id",
                "result": {
                    "prompt": "test prompt",
                    "scores": [
                        {
                            "name": "accuracy",
                            "value": 0.8,
                            "metrics": ["mock_metric"],
                            "metadata": {},
                        }
                    ],
                    "error": "test error",
                    "model_response": "test response",
                },
                "dataset_row": {"input": "test input"},
                "error": "record error",
                # No timestamp field
            }
        ]

        deserialized = deserialize_records(test_data)

        assert len(deserialized) == 1
        assert deserialized[0].result.error == "test error"
        assert deserialized[0].error == "record error"
        assert deserialized[0].timestamp == 0  # Default value when timestamp is missing


def test_recursive_map_edge_cases():
    """Test recursive_map with edge cases."""
    # Test with None
    assert recursive_map(None, str) == "None"

    # Test with empty structures
    assert recursive_map({}, str) == {}
    assert recursive_map([], str) == []
    assert recursive_map(set(), str) == set()
    assert recursive_map((), str) == ()


def test_serialize_deserialize_edge_cases():
    """Test edge cases in serialization."""
    from dotevals.utils import deserialize_value, serialize_value

    # Complex nested structure
    complex_data = {
        "none": None,
        "empty_list": [],
        "empty_dict": {},
        "nested": {"list": [None, 1, "test", []], "dict": {"a": None}},
    }

    serialized = serialize_value(complex_data)
    deserialized = deserialize_value(serialized)
    assert deserialized == complex_data

    # Test with nested empty structures
    assert recursive_map({"a": [], "b": {}}, str) == {"a": [], "b": {}}

    # Test with mixed types
    mixed_data = {"a": [1, "2", 3.0], "b": {"x": True, "y": None}}
    result = recursive_map(mixed_data, str)
    assert result == {"a": ["1", "2", "3.0"], "b": {"x": "True", "y": "None"}}
