"""Tests for the providers module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dotevals.providers import (
    ModelHandle,
    ModelProvider,
    discover_model_providers,
    model_providers,
)


class TestModelHandle:
    """Tests for ModelHandle class."""

    @pytest.mark.asyncio
    async def test_model_handle_teardown(self):
        """Test ModelHandle teardown calls manager's teardown method."""
        # Create a mock manager
        mock_manager = AsyncMock(spec=ModelProvider)

        # Create a handle
        handle = ModelHandle(
            resource_id="test_resource", model="test_model", manager=mock_manager
        )

        # Teardown should call manager's teardown
        await handle.teardown()

        mock_manager.teardown.assert_called_once_with("test_resource")
        assert not handle._active

    @pytest.mark.asyncio
    async def test_model_handle_multiple_teardown(self):
        """Test that multiple teardowns only call manager once."""
        # Create a mock manager
        mock_manager = AsyncMock(spec=ModelProvider)

        # Create a handle
        handle = ModelHandle(
            resource_id="test_resource", model="test_model", manager=mock_manager
        )

        # First teardown
        await handle.teardown()
        assert not handle._active
        mock_manager.teardown.assert_called_once_with("test_resource")

        # Second teardown should not call manager again
        await handle.teardown()
        mock_manager.teardown.assert_called_once()  # Still only once


class TestModelProvider:
    """Tests for ModelProvider abstract base class."""

    def test_model_provider_cannot_be_instantiated(self):
        """Test that ModelProvider ABC cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ModelProvider()

    @pytest.mark.asyncio
    async def test_model_provider_implementation(self):
        """Test implementing a concrete ModelProvider."""

        class TestProvider(ModelProvider):
            async def setup(self, resource_spec: str, **config) -> ModelHandle:
                return ModelHandle(
                    resource_id=f"test_{resource_spec}",
                    model=f"model_{resource_spec}",
                    manager=self,
                )

            async def teardown(self, resource_id: str) -> None:
                pass

        provider = TestProvider()
        handle = await provider.setup("gpt-4", temperature=0.7)

        assert handle.resource_id == "test_gpt-4"
        assert handle.model == "model_gpt-4"
        assert handle.manager is provider
        assert handle._active


class TestDiscoverModelProviders:
    """Tests for discover_model_providers function."""

    def test_discover_no_entry_points(self):
        """Test discovery when no entry points exist."""
        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = []

            providers = discover_model_providers()

            assert providers == {}

    def test_discover_with_valid_fixture(self):
        """Test discovery with a valid fixture entry point."""

        class MockEntryPoint:
            name = "test_provider"
            value = "test_module:test_fixture"

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [MockEntryPoint()]

            providers = discover_model_providers()

            assert "test_provider" in providers
            assert providers["test_provider"] == "test_fixture"

    def test_discover_with_processing_error(self):
        """Test discovery when processing entry point fails."""

        class FailingEntryPoint:
            name = "failing_provider"

            @property
            def value(self):
                raise AttributeError("Cannot access value")

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [FailingEntryPoint()]

            with patch("warnings.warn") as mock_warn:
                providers = discover_model_providers()

                assert providers == {}
                mock_warn.assert_called_once()
                assert "Failed to process model provider" in str(
                    mock_warn.call_args[0][0]
                )

    def test_discover_old_api_fallback(self):
        """Test fallback to old importlib API."""
        with patch("importlib.metadata.entry_points") as mock_ep:
            # First call raises TypeError (new API not available)
            # Second call returns dict (old API)
            mock_ep.side_effect = [
                TypeError("entry_points() got an unexpected keyword argument 'group'"),
                {"dotevals.model_providers": []},
            ]

            providers = discover_model_providers()

            assert providers == {}
            assert mock_ep.call_count == 2

    def test_discover_invalid_entry_point_format(self):
        """Test entry point with invalid format."""

        class MockEntryPoint:
            name = "test_provider"
            value = "no_colon_here"

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [MockEntryPoint()]

            providers = discover_model_providers()

            # Should still work, split will just return the whole string
            assert "test_provider" in providers
            assert providers["test_provider"] == "no_colon_here"

    def test_discover_multiple_providers(self):
        """Test discovering multiple providers."""

        class MockEntryPoint1:
            name = "provider1"
            value = "module1:fixture1"

        class MockEntryPoint2:
            name = "provider2"
            value = "module2:fixture2"

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [MockEntryPoint1(), MockEntryPoint2()]

            providers = discover_model_providers()

            assert len(providers) == 2
            assert "provider1" in providers
            assert "provider2" in providers
            assert providers["provider1"] == "fixture1"
            assert providers["provider2"] == "fixture2"


class TestModelProvidersFixture:
    """Tests for the model_providers fixture."""

    def test_model_providers_fixture_exists(self):
        """Test that model_providers fixture is exported."""
        from dotevals.providers import model_providers

        # Should be a pytest fixture
        assert hasattr(model_providers, "__wrapped__")
        assert model_providers.__name__ == "model_providers"

    @patch("dotevals.providers.discover_model_providers")
    def test_model_providers_fixture_discovery(self, mock_discover):
        """Test that model_providers fixture retrieves providers."""
        # Mock the discovered providers
        mock_discover.return_value = {"provider1": "fixture1", "provider2": "fixture2"}

        # Mock request object
        mock_request = MagicMock()
        mock_provider1 = MagicMock(spec=ModelProvider)
        mock_provider2 = MagicMock(spec=ModelProvider)

        def mock_getfixturevalue(name):
            if name == "fixture1":
                return mock_provider1
            elif name == "fixture2":
                return mock_provider2
            raise Exception(f"Unknown fixture: {name}")

        mock_request.getfixturevalue = mock_getfixturevalue

        # Import and call the wrapped function
        from dotevals.providers import model_providers

        result = model_providers.__wrapped__(mock_request)

        assert len(result) == 2
        assert result["provider1"] is mock_provider1
        assert result["provider2"] is mock_provider2

    @patch("dotevals.providers.discover_model_providers")
    @patch("warnings.warn")
    def test_model_providers_fixture_with_load_error(self, mock_warn, mock_discover):
        """Test model_providers fixture when a provider fails to load."""
        # Mock the discovered providers
        mock_discover.return_value = {
            "good_provider": "good_fixture",
            "bad_provider": "bad_fixture",
        }

        # Mock request object
        mock_request = MagicMock()
        mock_good_provider = MagicMock(spec=ModelProvider)

        def mock_getfixturevalue(name):
            if name == "good_fixture":
                return mock_good_provider
            elif name == "bad_fixture":
                raise Exception("Failed to load fixture")
            raise Exception(f"Unknown fixture: {name}")

        mock_request.getfixturevalue = mock_getfixturevalue

        # Import and call the wrapped function
        from dotevals.providers import model_providers

        result = model_providers.__wrapped__(mock_request)

        # Should only have the good provider
        assert len(result) == 1
        assert result["good_provider"] is mock_good_provider
        assert "bad_provider" not in result

        # Should have warned about the bad provider
        mock_warn.assert_called_once()
        assert "Failed to load model provider bad_provider" in str(
            mock_warn.call_args[0][0]
        )


class TestModelHandleActiveProperty:
    """Test ModelHandle is_active property."""

    def test_is_active_property(self):
        """Test is_active property returns correct state."""
        mock_manager = MagicMock(spec=ModelProvider)
        handle = ModelHandle(resource_id="test", model="model", manager=mock_manager)

        # Should be active initially
        assert handle.is_active
        assert handle._active

        # Set to inactive
        handle._active = False
        assert not handle.is_active


class TestProviderIntegration:
    """Integration tests for the providers module."""

    @pytest.mark.asyncio
    async def test_full_provider_lifecycle(self):
        """Test complete provider lifecycle from setup to teardown."""
        resources = {}

        class FullProvider(ModelProvider):
            async def setup(self, resource_spec: str, **config) -> ModelHandle:
                resource_id = f"resource_{len(resources)}"
                model = f"model_{resource_spec}"
                resources[resource_id] = model
                return ModelHandle(resource_id=resource_id, model=model, manager=self)

            async def teardown(self, resource_id: str) -> None:
                if resource_id in resources:
                    del resources[resource_id]

        provider = FullProvider()

        # Setup multiple resources
        handle1 = await provider.setup("gpt-4")
        handle2 = await provider.setup("claude")

        assert len(resources) == 2
        assert handle1.model == "model_gpt-4"
        assert handle2.model == "model_claude"

        # Teardown one resource
        await handle1.teardown()
        assert len(resources) == 1
        assert "resource_0" not in resources

        # Teardown second resource
        await handle2.teardown()
        assert len(resources) == 0

    def test_old_api_fallback_with_dict(self):
        """Test old API fallback when entry_points returns a dict."""
        from dotevals.providers import discover_model_providers

        class MockEntryPoint:
            name = "old_provider"
            value = "old_module:old_fixture"

        # Mock the new API to raise TypeError
        # Then mock the old API to return a dict
        with patch("importlib.metadata.entry_points") as mock_ep:
            # First call raises TypeError (new API not available)
            # Second call returns dict (old API)
            mock_ep.side_effect = [
                TypeError("entry_points() got an unexpected keyword argument 'group'"),
                {"dotevals.model_providers": [MockEntryPoint()]},
            ]

            providers = discover_model_providers()

            assert "old_provider" in providers
            assert providers["old_provider"] == "old_fixture"

    @patch("dotevals.providers.discover_model_providers")
    def test_model_providers_fixture_no_getfixturevalue(self, mock_discover):
        """Test model_providers fixture when request doesn't have getfixturevalue."""
        # Mock the discovered providers
        mock_discover.return_value = {"provider1": "fixture1"}

        # Mock request object without getfixturevalue
        mock_request = MagicMock()
        del mock_request.getfixturevalue  # Remove the attribute

        # Call the wrapped function
        result = model_providers.__wrapped__(mock_request)

        # Should return empty dict when getfixturevalue is not available
        assert result == {}
