"""
Shared utility functions for dotevals.

This module contains common functionality used across multiple components,
particularly serialization logic shared between storage backends.
"""

import base64
import io
from collections.abc import Callable
from typing import Any

from PIL import Image

from dotevals.models import Record, Result, Score


def recursive_map(obj: Any, transform_func: Callable[[Any], Any]) -> Any:
    """
    Recursively apply a transformation function to all values in a nested structure.

    This function traverses through dictionaries, lists, sets, and tuples,
    applying the transform_func to each value it encounters.

    Args:
        obj: The object to transform
        transform_func: Function to apply to each value

    Returns:
        The object with all values transformed by transform_func
    """
    if isinstance(obj, dict):
        return {k: recursive_map(v, transform_func) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_map(x, transform_func) for x in obj]
    elif isinstance(obj, set):
        return {recursive_map(x, transform_func) for x in obj}
    elif isinstance(obj, tuple):
        return tuple(recursive_map(x, transform_func) for x in obj)
    else:
        return transform_func(obj)


def serialize_value(value: Any) -> Any:
    """Recursively serialize values, converting PIL Images to base64.

    This function handles the conversion of complex Python objects into
    JSON-serializable formats, with special handling for PIL Images.

    Args:
        value: The value to serialize

    Returns:
        A JSON-serializable representation of the value
    """
    if isinstance(value, Image.Image):
        # Convert PIL Image to base64
        buffered = io.BytesIO()
        value.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        return {
            "__type__": "PIL.Image",
            "data": img_base64,
            "mode": value.mode,
            "size": value.size,
        }
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return {"__type__": "tuple", "data": [serialize_value(item) for item in value]}
    elif isinstance(value, set):
        return {"__type__": "set", "data": [serialize_value(item) for item in value]}
    else:
        return value


def deserialize_value(value: Any) -> Any:
    """Recursively deserialize values, converting base64 back to PIL Images.

    This function reverses the serialization process, reconstructing
    complex Python objects from their JSON-serializable representations.

    Args:
        value: The serialized value to deserialize

    Returns:
        The original Python object
    """
    if isinstance(value, dict):
        if value.get("__type__") == "PIL.Image":
            # Convert base64 back to PIL Image
            img_data = base64.b64decode(value["data"])
            img = Image.open(io.BytesIO(img_data))
            return img
        elif value.get("__type__") == "tuple":
            return tuple(deserialize_value(item) for item in value["data"])
        elif value.get("__type__") == "set":
            return {deserialize_value(item) for item in value["data"]}
        else:
            return {k: deserialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [deserialize_value(item) for item in value]
    else:
        return value


def serialize_records(results: list[Record]) -> list[dict]:
    """Serialize a list of Record objects to JSON-compatible dictionaries.

    Args:
        results: List of Record objects to serialize

    Returns:
        List of dictionaries representing the serialized records
    """
    data = [
        {
            "item_id": r.item_id,
            "result": {
                "prompt": r.result.prompt,
                "scores": [
                    {
                        "name": s.name,
                        "value": s.value,
                        "metrics": [metric.__name__ for metric in s.metrics],
                        "metadata": s.metadata,
                    }
                    for s in r.result.scores
                ],
                "error": r.result.error,
                "model_response": r.result.model_response,
            },
            "dataset_row": serialize_value(r.dataset_row),
            "error": r.error,
            "timestamp": r.timestamp,
        }
        for r in results
    ]

    return data


def deserialize_records(data: list[dict]) -> list[Record]:
    """Deserialize a list of dictionaries back to Record objects.

    Args:
        data: List of dictionaries representing serialized records

    Returns:
        List of Record objects
    """
    from dotevals.metrics import registry

    results = []
    for r_data in data:
        scores = [
            Score(
                name=s_data["name"],
                value=s_data["value"],
                metrics=[registry[metric_name] for metric_name in s_data["metrics"]],
                metadata=s_data.get("metadata", {}),
            )
            for s_data in r_data["result"]["scores"]
        ]

        result = Result(
            *scores,
            prompt=r_data["result"].get("prompt"),
            error=r_data["result"].get("error"),
            model_response=r_data["result"].get("model_response"),
        )

        record = Record(
            result=result,
            item_id=r_data["item_id"],
            dataset_row=deserialize_value(r_data["dataset_row"]),
            error=r_data.get("error"),
            timestamp=r_data.get("timestamp") or 0,
        )

        results.append(record)

    return results
