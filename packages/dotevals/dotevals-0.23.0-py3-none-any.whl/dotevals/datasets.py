"""Dataset base class and plugin system for dotevals.

This module provides a plugin-based system for loading and managing datasets
in dotevals. Datasets can be registered via entry points, allowing third-party
packages to provide custom datasets that integrate seamlessly with dotevals's
@foreach decorator.

The plugin system uses Python's entry points mechanism to discover and load
datasets at runtime. This allows for:
- Dynamic dataset discovery without modifying dotevals core
- Easy distribution of custom datasets as separate packages
- Lazy loading of dataset implementations

Examples:
    To use a registered dataset:

    ```python
    from dotevals import foreach

    @foreach.gsm8k("test")
    def eval_math(question, reasoning, answer, model):
        response = model.solve(question)
        return numeric_match(response, answer)
    ```

To create a custom dataset plugin, implement the Dataset ABC and register
it via entry points in your package's pyproject.toml.
"""

import importlib.metadata
import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, Optional


class Dataset(ABC):
    """Abstract base class for all dotevals datasets.

    All dataset plugins must inherit from this class and implement the required
    methods and attributes. Datasets are expected to be iterable and yield
    tuples of data that match the columns specification.

    Attributes:
        name: Unique identifier for the dataset (e.g., "gsm8k", "bfcl")
        splits: list of available data splits (e.g., ["train", "test", "validation"])
        columns: list of column names that will be yielded in order (e.g., ["question", "answer"])
        num_rows: Optional total number of rows in the dataset. Can be None for
                 streaming datasets or when the size is unknown.

    Examples:
        Creating a dataset with splits:

        ```python
        class MyDataset(Dataset):
            name = "my_dataset"
            splits = ["train", "test"]
            columns = ["input", "output"]

            def __init__(self, split: str | None = None, **kwargs):
                if split is None:
                    raise ValueError("This dataset requires a split")
                self.split = split
                self.data = self._load_data(split)
                self.num_rows = len(self.data)

            def __iter__(self):
                for item in self.data:
                    yield (item["input"], item["output"])
        ```

        Creating a dataset without splits:

        ```python
        class SimpleDataset(Dataset):
            name = "simple_dataset"
            splits = []  # No splits
            columns = ["question", "answer"]

            def __init__(self, split: str | None = None, **kwargs):
                # Ignore split parameter since this dataset has no splits
                self.data = self._load_all_data()
                self.num_rows = len(self.data)

            def __iter__(self):
                for item in self.data:
                    yield (item["question"], item["answer"])
        ```
    """

    name: str
    splits: list[str]
    columns: list[str]
    num_rows: int | None = None

    @abstractmethod
    def __init__(self, split: str | None = None, **kwargs: Any) -> None:
        """Initialize the dataset with the specified split.

        This method should load or prepare access to the dataset data.
        For large datasets, consider implementing lazy loading or streaming
        to avoid loading all data into memory at once.

        Args:
            split: The dataset split to load (must be one of the values in self.splits).
                  Can be None for datasets that don't have splits.
            **kwargs: Additional dataset-specific parameters

        Raises:
            ValueError: If the split is not valid for this dataset
            IOError: If the dataset files cannot be loaded
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[tuple]:
        """Iterate over dataset items.

        Each iteration should yield a tuple with values corresponding to
        the columns defined in self.columns. The order of values in the
        tuple must match the order of column names.

        Yields:
            tuple containing one value for each column in self.columns

        Examples:
            If self.columns = ["question", "answer"], then each yield
            should be a 2-tuple like ("What is 2+2?", "4")
        """
        pass


class DatasetRegistry:
    """Central registry for managing dataset plugins.

    The DatasetRegistry is responsible for discovering, loading, and managing
    dataset plugins. It uses Python's entry points mechanism to dynamically
    discover datasets installed in the Python environment.

    The registry follows a lazy discovery pattern - plugins are only discovered
    when first needed, reducing startup time. Once discovered, dataset classes
    are cached for efficient access.

    Entry points should be registered in the "dotevals.datasets" group.

    Examples:
        In your package's pyproject.toml:

        ```toml
        [project.entry-points."dotevals.datasets"]
        my_dataset = "my_package.datasets:MyDataset"
        ```

    Attributes:
        _dataset_classes: Dictionary mapping dataset names to their classes
        _discovery_completed: Flag indicating whether plugin discovery has been performed.
            This is necessary because an empty _dataset_classes could mean either
            "not discovered yet" or "discovered but no plugins found".
    """

    def __init__(self):
        self._dataset_classes: dict[str, type[Dataset]] = {}  # type: ignore[attr-defined]
        # Track whether discovery has been performed, even if no plugins were found
        self._discovery_completed = False

    def discover_plugins(self, force: bool = False) -> None:
        """Discover and load all installed dataset plugins.

        This method scans for entry points in the "dotevals.datasets" group
        and loads the corresponding dataset classes. Invalid plugins (those
        that don't inherit from Dataset) are skipped with a warning.

        The discovery process is cached - subsequent calls will not re-discover
        unless force=True is specified.

        Args:
            force: If True, force re-discovery even if already performed.
                  Useful for testing or when plugins may have been installed
                  after the initial discovery.

        Note:
            Discovery happens automatically when needed (e.g., when calling
            get_dataset_class or list_datasets), so manual calls to this
            method are typically not necessary.
        """
        if self._discovery_completed and not force:
            return

        # Discover from entry points
        try:
            # Try the new API first (Python 3.10+)
            dataset_entry_points = importlib.metadata.entry_points(
                group="dotevals.datasets"
            )
        except TypeError:
            # Fall back to older API
            entry_points = importlib.metadata.entry_points()
            dataset_entry_points = entry_points.get("dotevals.datasets", [])  # type: ignore[attr-defined, arg-type]

        for entry_point in dataset_entry_points:
            try:
                dataset_class = entry_point.load()

                if not issubclass(dataset_class, Dataset):
                    plugin_name = getattr(entry_point, "name", str(entry_point))
                    warnings.warn(f"Plugin {plugin_name} does not inherit from Dataset")
                    continue

                self.register(dataset_class)

            except Exception as e:
                plugin_name = getattr(entry_point, "name", str(entry_point))
                warnings.warn(f"Failed to load plugin {plugin_name}: {e}")

        self._discovery_completed = True

    def register(self, dataset_class: type[Dataset]):
        """Register a dataset class in the registry.

        This method can be used to manually register dataset classes without
        using the entry points mechanism. This is useful for testing or for
        registering datasets dynamically at runtime.

        The registration is idempotent - registering the same class multiple
        times has no effect. However, attempting to register a different class
        with the same name will raise an error.

        Args:
            dataset_class: A class that inherits from Dataset and has all
                          required attributes (name, splits, columns)

        Raises:
            ValueError: If a different class is already registered with the
                       same name as dataset_class.name
            AttributeError: If dataset_class lacks required attributes
        """
        name = dataset_class.name
        if name in self._dataset_classes:
            # Allow re-registration of the same class (idempotent)
            if self._dataset_classes[name] is dataset_class:
                return
            raise ValueError(
                f"Tried to register {name}, but it was already registered with a different class."
            )
        self._dataset_classes[name] = dataset_class

    def get_dataset_class(self, name: str) -> type[Dataset]:
        """Retrieve a dataset class by its name.

        This method will trigger plugin discovery if it hasn't been performed
        yet. The returned class can be instantiated to create a dataset instance.

        Args:
            name: The name of the dataset (as defined by the Dataset.name attribute)

        Returns:
            The Dataset class corresponding to the given name

        Raises:
            ValueError: If no dataset with the given name is found

        Examples:
            ```python
            >>> dataset_cls = registry.get_dataset_class("gsm8k")
            >>> dataset = dataset_cls(split="test")
            ```
        """
        self.discover_plugins()

        if name not in self._dataset_classes:
            raise ValueError(
                f"Dataset '{name}' not found. "
                f"Available datasets: {self.list_datasets()}"
            )
        return self._dataset_classes[name]

    def list_datasets(self) -> list[str]:
        """list all available dataset names.

        This method will trigger plugin discovery if it hasn't been performed
        yet. The returned names can be used with get_dataset_class() or with
        the @foreach.dataset_name() decorator syntax.

        Returns:
            list of registered dataset names, sorted alphabetically

        Examples:
            ```python
            >>> available = registry.list_datasets()
            >>> print(available)
            ['bfcl', 'gsm8k', 'sroie']
            ```
        """
        self.discover_plugins()
        return list(self._dataset_classes.keys())


# Global registry instance
_registry = DatasetRegistry()


def list_available() -> list[str]:
    """list all available datasets that can be used with @foreach decorator.

    This function provides a convenient way to discover what datasets are
    available in the current environment. The returned dataset names can be
    used with the @foreach decorator using the syntax @foreach.dataset_name().

    Returns:
        list of dataset names sorted alphabetically

    Examples:
        ```python
        >>> from dotevals.datasets import list_available
        >>> datasets = list_available()
        >>> print(datasets)
        ['bfcl', 'gsm8k', 'sroie']

        # Use discovered dataset
        >>> from dotevals import foreach
        >>> @foreach.gsm8k("test")
        ... def evaluate(question, reasoning, answer, model):
        ...     # evaluation logic
        ...     pass
        ```

    See Also:
        get_dataset_info: Get detailed information about a specific dataset
    """
    return _registry.list_datasets()


def get_dataset_info(name: str) -> dict:
    """Get detailed information about a specific dataset.

    This function retrieves metadata about a dataset without instantiating it.
    Useful for understanding what columns a dataset provides and what splits
    are available before using it in evaluations.

    Args:
        name: The name of the dataset to get information about

    Returns:
        Dictionary containing:
            - name (str): The dataset's name
            - splits (list[str]): Available data splits (empty list if no splits)
            - columns (list[str]): Column names that will be provided
            - num_rows (int | None): Total rows if known, None otherwise

    Raises:
        ValueError: If the dataset name is not found

    Examples:
        ```python
        >>> from dotevals.datasets import get_dataset_info
        >>> info = get_dataset_info("gsm8k")
        >>> print(info)
        {
            'name': 'gsm8k',
            'splits': ['train', 'test'],
            'columns': ['question', 'reasoning', 'answer'],
            'num_rows': None
        }

        # Use this info to understand the dataset structure
        >>> @foreach.gsm8k("test")
        ... def evaluate(question, reasoning, answer, model):
        ...     # We know we'll receive these three columns
        ...     pass
        ```

    See Also:
        list_available: Discover all available datasets
    """
    dataset_class = _registry.get_dataset_class(name)
    return {
        "name": dataset_class.name,
        "splits": getattr(dataset_class, "splits", []),
        "columns": dataset_class.columns,
        "num_rows": getattr(dataset_class, "num_rows", None),
    }
