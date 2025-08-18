"""Concurrency strategies for dotevals."""

from typing import Union

from .adaptive import Adaptive
from .async_sequential import AsyncSequential
from .batch import Batch
from .sequential import Sequential
from .sliding_window import SlidingWindow

# Backward compatibility aliases (will be deprecated in future versions)
SyncConcurrencyStrategy = Batch | Sequential
AsyncConcurrencyStrategy = SlidingWindow | Adaptive | AsyncSequential

__all__ = [
    "Adaptive",
    "AsyncSequential",
    "Batch",
    "Sequential",
    "SlidingWindow",
    # Type unions
    "SyncConcurrencyStrategy",
    "AsyncConcurrencyStrategy",
]
