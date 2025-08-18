"""Tests for dataset module and plugin system."""

from unittest.mock import MagicMock, patch

import pytest

from dotevals.datasets import (
    Dataset,
    DatasetRegistry,
    _registry,
    get_dataset_info,
    list_available,
)


class MockDataset(Dataset):
    """Mock dataset for testing."""

    name = "mock_dataset"
    splits = ["train", "test"]
    columns = ["input", "output"]

    def __init__(self, split: str, **kwargs):
        self.split = split
        self.num_rows = 10

    def __iter__(self):
        for i in range(self.num_rows):
            yield (f"input_{i}", f"output_{i}")


class TestDatasetRegistry:
    """Test DatasetRegistry functionality."""

    def test_register_dataset(self):
        """Test registering a dataset."""
        registry = DatasetRegistry()
        registry.register(MockDataset)

        assert "mock_dataset" in registry._dataset_classes
        assert registry._dataset_classes["mock_dataset"] is MockDataset

    def test_register_duplicate_idempotent(self):
        """Test that re-registering the same class is idempotent."""
        registry = DatasetRegistry()
        registry.register(MockDataset)
        registry.register(MockDataset)  # Should not raise

        assert registry._dataset_classes["mock_dataset"] is MockDataset

    def test_register_duplicate_different_class_raises(self):
        """Test that registering different class with same name raises."""

        class AnotherMockDataset(Dataset):
            name = "mock_dataset"
            splits = ["train"]
            columns = ["x"]

            def __init__(self, split: str, **kwargs):
                pass

            def __iter__(self):
                pass

        registry = DatasetRegistry()
        registry.register(MockDataset)

        with pytest.raises(
            ValueError, match="already registered with a different class"
        ):
            registry.register(AnotherMockDataset)

    def test_get_dataset_class(self):
        """Test getting a dataset class."""
        registry = DatasetRegistry()
        registry.register(MockDataset)

        dataset_class = registry.get_dataset_class("mock_dataset")
        assert dataset_class is MockDataset

    def test_get_dataset_class_not_found(self):
        """Test getting non-existent dataset raises."""
        registry = DatasetRegistry()

        with pytest.raises(ValueError, match="Dataset 'nonexistent' not found"):
            registry.get_dataset_class("nonexistent")

    def test_list_datasets(self):
        """Test listing datasets."""
        registry = DatasetRegistry()
        registry.register(MockDataset)

        datasets = registry.list_datasets()
        assert "mock_dataset" in datasets


class TestDatasetPluginSystem:
    """Test the plugin discovery system."""

    def test_discover_plugins(self):
        """Test plugin discovery via entry points."""
        # Create mock entry points
        mock_entry_point = MagicMock()
        mock_entry_point.name = "plugin_dataset"
        mock_entry_point.load.return_value = MockDataset

        with patch("importlib.metadata.entry_points") as mock_entry_points:
            # Mock the entry_points return value to match the actual API
            mock_entry_points.return_value = [mock_entry_point]

            registry = DatasetRegistry()
            registry.discover_plugins()

            # Should have discovered and registered the dataset
            assert "mock_dataset" in registry._dataset_classes
            assert registry._discovery_completed is True

    def test_discover_plugins_invalid_dataset(self):
        """Test that invalid datasets are skipped with warning."""

        # Create a class that doesn't inherit from Dataset
        class NotADataset:
            pass

        mock_entry_point = MagicMock()
        mock_entry_point.name = "invalid_dataset"
        mock_entry_point.load.return_value = NotADataset

        with patch("importlib.metadata.entry_points") as mock_entry_points:
            mock_entry_points.return_value = [mock_entry_point]

            registry = DatasetRegistry()

            with pytest.warns(UserWarning, match="does not inherit from Dataset"):
                registry.discover_plugins()

            # Should not have registered the invalid dataset
            assert "invalid_dataset" not in registry._dataset_classes

    def test_discover_plugins_load_error(self):
        """Test that plugin load errors are handled gracefully."""
        mock_entry_point = MagicMock()
        mock_entry_point.name = "error_dataset"
        mock_entry_point.load.side_effect = ImportError("Failed to import")

        with patch("importlib.metadata.entry_points") as mock_entry_points:
            mock_entry_points.return_value = [mock_entry_point]

            registry = DatasetRegistry()

            with pytest.warns(UserWarning, match="Failed to load plugin"):
                registry.discover_plugins()

    def test_discover_plugins_force(self):
        """Test force rediscovery of plugins."""
        mock_entry_point = MagicMock()
        mock_entry_point.name = "plugin_dataset"
        mock_entry_point.load.return_value = MockDataset

        with patch("importlib.metadata.entry_points") as mock_entry_points:
            mock_entry_points.return_value = [mock_entry_point]

            registry = DatasetRegistry()
            registry.discover_plugins()

            # Clear the registry manually
            registry._dataset_classes.clear()

            # Without force, should not rediscover
            registry.discover_plugins()
            assert len(registry._dataset_classes) == 0

            # With force, should rediscover
            registry.discover_plugins(force=True)
            assert "mock_dataset" in registry._dataset_classes

    def test_discover_plugins_already_discovered_early_return(self):
        """Test that discover_plugins returns early when already discovered."""
        registry = DatasetRegistry()

        # Set as already discovered
        registry._discovery_completed = True

        with patch("importlib.metadata.entry_points") as mock_entry_points:
            # This should never be called due to early return
            mock_entry_points.return_value = []

            registry.discover_plugins()

            # entry_points should not have been called
            mock_entry_points.assert_not_called()


class TestDatasetHelperFunctions:
    """Test the helper functions."""

    def test_list_available(self):
        """Test list_available function."""
        with patch.object(
            _registry, "list_datasets", return_value=["dataset1", "dataset2"]
        ):
            datasets = list_available()
            assert datasets == ["dataset1", "dataset2"]

    def test_get_dataset_info(self):
        """Test get_dataset_info function."""
        with patch.object(_registry, "get_dataset_class", return_value=MockDataset):
            info = get_dataset_info("mock_dataset")

            assert info["name"] == "mock_dataset"
            assert info["splits"] == ["train", "test"]
            assert info["columns"] == ["input", "output"]
            assert (
                info["num_rows"] is None
            )  # MockDataset doesn't have class-level num_rows


class TestDatasetBase:
    """Test the Dataset base class."""

    def test_dataset_abstract_methods(self):
        """Test that Dataset enforces abstract methods."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Dataset()

    def test_dataset_implementation(self):
        """Test a concrete dataset implementation."""
        dataset = MockDataset("train")

        assert dataset.split == "train"
        assert dataset.num_rows == 10

        # Test iteration
        items = list(dataset)
        assert len(items) == 10
        assert items[0] == ("input_0", "output_0")
        assert items[-1] == ("input_9", "output_9")

    def test_dataset_abstract_init(self):
        """Test that Dataset.__init__ is abstract."""

        # Create a dataset that doesn't implement __init__
        class BadDataset(Dataset):
            name = "bad"
            splits = []
            columns = []

            def __iter__(self):
                yield from []

        with pytest.raises(TypeError, match="abstract method"):
            BadDataset("train")

    def test_dataset_abstract_iter(self):
        """Test that Dataset.__iter__ is abstract."""

        # Create a dataset that doesn't implement __iter__
        class BadDataset(Dataset):
            name = "bad"
            splits = []
            columns = []

            def __init__(self, split: str, **kwargs):
                pass

        with pytest.raises(TypeError, match="abstract method"):
            BadDataset("train")

    def test_discover_plugins_old_api(self):
        """Test the TypeError fallback path in discover_plugins."""
        registry = DatasetRegistry()

        # Create a mock that simulates old API behavior
        with patch("importlib.metadata.entry_points") as mock_ep:
            # First call raises TypeError (new API not supported)
            # Second call returns dict (old API)
            mock_ep.side_effect = [
                TypeError("entry_points() got an unexpected keyword argument 'group'"),
                {"dotevals.datasets": []},  # Old API returns dict
            ]

            registry.discover_plugins(force=True)
            assert registry._discovery_completed is True
            assert mock_ep.call_count == 2

    def test_registry_initialization(self):
        """Test DatasetRegistry initialization."""
        registry = DatasetRegistry()
        assert registry._dataset_classes == {}
        assert registry._discovery_completed is False


def test_get_dataset_info_handles_missing_splits():
    """Test that get_dataset_info handles datasets without splits attribute."""
    from dotevals.datasets import get_dataset_info

    # Create a dataset class without splits attribute
    class NoSplitsDataset(Dataset):
        name = "no_splits_test"
        columns = ["input", "output"]
        # No splits attribute defined

        def __init__(self, **kwargs):
            pass

        def __iter__(self):
            yield ("test", "output")

    # Mock the registry to return our test dataset
    with patch.object(_registry, "get_dataset_class", return_value=NoSplitsDataset):
        info = get_dataset_info("no_splits_test")

        assert info["name"] == "no_splits_test"
        assert info["splits"] == []  # Should default to empty list
        assert info["columns"] == ["input", "output"]
        assert info["num_rows"] is None


def test_get_dataset_info_preserves_existing_splits():
    """Test that get_dataset_info preserves existing splits attribute."""
    from dotevals.datasets import get_dataset_info

    # Create a dataset class with splits attribute
    class WithSplitsDataset(Dataset):
        name = "with_splits_test"
        splits = ["train", "test", "validation"]
        columns = ["question", "answer"]

        def __init__(self, split, **kwargs):
            self.split = split

        def __iter__(self):
            yield ("test question", "test answer")

    # Mock the registry to return our test dataset
    with patch.object(_registry, "get_dataset_class", return_value=WithSplitsDataset):
        info = get_dataset_info("with_splits_test")

        assert info["name"] == "with_splits_test"
        assert info["splits"] == ["train", "test", "validation"]
        assert info["columns"] == ["question", "answer"]
        assert info["num_rows"] is None
