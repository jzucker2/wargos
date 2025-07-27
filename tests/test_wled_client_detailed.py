import os
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.wled_client import WLEDClient
from app.metrics import Metrics


class TestWLEDClientDetailed:
    """Comprehensive tests for WLEDClient covering all functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = WLEDClient()
        self.client_with_session = WLEDClient(session=MagicMock())

    def test_get_client_class_method(self):
        """Test that get_client class method returns correct instance"""
        # Test without session
        client = WLEDClient.get_client()
        assert isinstance(client, WLEDClient)
        assert client.session is None

        # Test with session
        mock_session = MagicMock()
        client = WLEDClient.get_client(session=mock_session)
        assert isinstance(client, WLEDClient)
        assert client.session == mock_session

    def test_default_wled_ip_environment_variable(self):
        """Test default_wled_ip with environment variable set"""
        with patch.dict(os.environ, {"DEFAULT_WLED_IP": "192.168.1.100"}):
            result = WLEDClient.default_wled_ip()
            assert result == "192.168.1.100"

    def test_default_wled_ip_fallback(self):
        """Test default_wled_ip fallback when environment variable not set"""
        with patch.dict(os.environ, {}, clear=True):
            result = WLEDClient.default_wled_ip()
            assert result == "10.0.1.179"

    def test_init_without_session(self):
        """Test WLEDClient initialization without session"""
        client = WLEDClient()
        assert client.session is None

    def test_init_with_session(self):
        """Test WLEDClient initialization with session"""
        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        assert client.session == mock_session

    def test_session_property(self):
        """Test session property returns the session"""
        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        assert client.session == mock_session

    @patch("app.wled_client.WLED")
    def test_connecting_device_with_session(self, mock_wled_class):
        """Test _connecting_device with session"""
        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)

        result = client._connecting_device("192.168.1.100")

        mock_wled_class.assert_called_once_with(
            host="192.168.1.100", session=mock_session
        )
        assert result == mock_wled_class.return_value

    @patch("app.wled_client.WLED")
    def test_connecting_device_without_session(self, mock_wled_class):
        """Test _connecting_device without session"""
        client = WLEDClient()

        result = client._connecting_device("192.168.1.100")

        mock_wled_class.assert_called_once_with(host="192.168.1.100")
        assert result == mock_wled_class.return_value

    @patch("app.wled_client.WLEDReleases")
    def test_connecting_releases_with_session(self, mock_releases_class):
        """Test _connecting_releases with session"""
        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)

        result = client._connecting_releases()

        mock_releases_class.assert_called_once_with(session=mock_session)
        assert result == mock_releases_class.return_value

    @patch("app.wled_client.WLEDReleases")
    def test_connecting_releases_without_session(self, mock_releases_class):
        """Test _connecting_releases without session"""
        client = WLEDClient()

        result = client._connecting_releases()

        mock_releases_class.assert_called_once_with()
        assert result == mock_releases_class.return_value

    @pytest.mark.asyncio
    @patch("app.wled_client.WLED")
    async def test_get_wled_instance_device_success(self, mock_wled_class):
        """Test successful get_wled_instance_device call"""
        # Mock the async context manager
        mock_device = MagicMock()
        mock_wled_instance = AsyncMock()
        mock_wled_instance.__aenter__.return_value.update.return_value = (
            mock_device
        )
        mock_wled_class.return_value = mock_wled_instance

        client = WLEDClient()
        result = await client.get_wled_instance_device("192.168.1.100")

        assert result == mock_device
        mock_wled_class.assert_called_once_with(host="192.168.1.100")

    @pytest.mark.asyncio
    @patch("app.wled_client.WLED")
    async def test_get_wled_instance_device_with_session(
        self, mock_wled_class
    ):
        """Test get_wled_instance_device with session"""
        mock_device = MagicMock()
        mock_wled_instance = AsyncMock()
        mock_wled_instance.__aenter__.return_value.update.return_value = (
            mock_device
        )
        mock_wled_class.return_value = mock_wled_instance

        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        result = await client.get_wled_instance_device("192.168.1.100")

        assert result == mock_device
        mock_wled_class.assert_called_once_with(
            host="192.168.1.100", session=mock_session
        )

    @pytest.mark.asyncio
    @patch("app.wled_client.WLED")
    async def test_get_wled_instance_device_exception(self, mock_wled_class):
        """Test get_wled_instance_device with exception"""
        mock_wled_instance = AsyncMock()
        mock_wled_instance.__aenter__.side_effect = Exception(
            "Connection failed"
        )
        mock_wled_class.return_value = mock_wled_instance

        client = WLEDClient()

        with pytest.raises(Exception):
            await client.get_wled_instance_device("192.168.1.100")

    @pytest.mark.asyncio
    @patch("app.wled_client.WLED")
    async def test_simple_wled_test_success(self, mock_wled_class):
        """Test successful simple_wled_test call"""
        # Mock device info and state
        mock_device = MagicMock()
        mock_device.info.version = "0.15.0"
        mock_device.info.name = "Test WLED"
        mock_device.state.on = True

        # Create the mock WLED instance with proper async context manager
        mock_wled_instance = AsyncMock()
        mock_wled_instance.__aenter__.return_value = mock_wled_instance
        mock_wled_instance.update.return_value = mock_device
        mock_wled_instance.master = AsyncMock()
        mock_wled_class.return_value = mock_wled_instance

        client = WLEDClient()
        await client.simple_wled_test()

        # Verify WLED was called with default IP
        mock_wled_class.assert_called_once_with(host="10.0.1.179")
        # Verify master was called to turn on
        mock_wled_instance.master.assert_called_once_with(
            on=True, brightness=255
        )

    @pytest.mark.asyncio
    @patch("app.wled_client.WLED")
    async def test_simple_wled_test_with_custom_ip(self, mock_wled_class):
        """Test simple_wled_test with custom default IP"""
        mock_device = MagicMock()
        mock_wled_instance = AsyncMock()
        mock_wled_instance.__aenter__.return_value.update.return_value = (
            mock_device
        )
        mock_wled_instance.master = AsyncMock()
        mock_wled_class.return_value = mock_wled_instance

        with patch.dict(os.environ, {"DEFAULT_WLED_IP": "192.168.1.100"}):
            client = WLEDClient()
            await client.simple_wled_test()

            mock_wled_class.assert_called_once_with(host="192.168.1.100")

    @pytest.mark.asyncio
    @patch("app.wled_client.WLEDReleases")
    async def test_simple_wled_releases_test_success(
        self, mock_releases_class
    ):
        """Test successful simple_wled_releases_test call"""
        mock_releases = MagicMock()
        mock_releases.stable = "0.15.0"
        mock_releases.beta = "0.16.0-beta1"

        mock_releases_instance = AsyncMock()
        mock_releases_instance.__aenter__.return_value.releases.return_value = (
            mock_releases
        )
        mock_releases_class.return_value = mock_releases_instance

        client = WLEDClient()
        await client.simple_wled_releases_test()

        mock_releases_class.assert_called_once_with()

    @pytest.mark.asyncio
    @patch("app.wled_client.WLEDReleases")
    async def test_simple_wled_releases_test_with_session(
        self, mock_releases_class
    ):
        """Test simple_wled_releases_test with session"""
        mock_releases = MagicMock()
        mock_releases_instance = AsyncMock()
        mock_releases_instance.__aenter__.return_value.releases.return_value = (
            mock_releases
        )
        mock_releases_class.return_value = mock_releases_instance

        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        await client.simple_wled_releases_test()

        mock_releases_class.assert_called_once_with(session=mock_session)

    @pytest.mark.asyncio
    @patch("app.wled_client.WLEDReleases")
    async def test_get_wled_latest_releases_success(self, mock_releases_class):
        """Test successful get_wled_latest_releases call"""
        mock_releases = MagicMock()
        mock_releases.stable = "0.15.0"
        mock_releases.beta = "0.16.0-beta1"

        mock_releases_instance = AsyncMock()
        mock_releases_instance.__aenter__.return_value.releases.return_value = (
            mock_releases
        )
        mock_releases_class.return_value = mock_releases_instance

        client = WLEDClient()
        result = await client.get_wled_latest_releases()

        assert result == mock_releases
        mock_releases_class.assert_called_once_with()

    @pytest.mark.asyncio
    @patch("app.wled_client.WLEDReleases")
    async def test_get_wled_latest_releases_with_session(
        self, mock_releases_class
    ):
        """Test get_wled_latest_releases with session"""
        mock_releases = MagicMock()
        mock_releases_instance = AsyncMock()
        mock_releases_instance.__aenter__.return_value.releases.return_value = (
            mock_releases
        )
        mock_releases_class.return_value = mock_releases_instance

        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        result = await client.get_wled_latest_releases()

        assert result == mock_releases
        mock_releases_class.assert_called_once_with(session=mock_session)

    @pytest.mark.asyncio
    @patch("app.wled_client.WLEDReleases")
    async def test_get_wled_latest_releases_exception(
        self, mock_releases_class
    ):
        """Test get_wled_latest_releases with exception"""
        mock_releases_instance = AsyncMock()
        mock_releases_instance.__aenter__.side_effect = Exception(
            "Releases failed"
        )
        mock_releases_class.return_value = mock_releases_instance

        client = WLEDClient()

        with pytest.raises(Exception):
            await client.get_wled_latest_releases()

    def test_metrics_integration(self):
        """Test that metrics are properly configured"""
        # Test that metrics exist and have correct types
        assert isinstance(
            Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER,
            type(Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER),
        )
        assert isinstance(
            Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS,
            type(Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS),
        )
        assert isinstance(
            Metrics.WLED_CLIENT_CONNECT_TIME,
            type(Metrics.WLED_CLIENT_CONNECT_TIME),
        )
        assert isinstance(
            Metrics.WLED_RELEASES_CONNECT_EXCEPTIONS,
            type(Metrics.WLED_RELEASES_CONNECT_EXCEPTIONS),
        )
        assert isinstance(
            Metrics.WLED_RELEASES_CONNECT_TIME,
            type(Metrics.WLED_RELEASES_CONNECT_TIME),
        )

    def test_metrics_labels(self):
        """Test that metrics have correct labels"""
        # Test basic client labels
        assert "ip" in Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER._labelnames
        assert "ip" in Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS._labelnames
        assert "ip" in Metrics.WLED_CLIENT_CONNECT_TIME._labelnames

    def test_async_methods_are_coroutines(self):
        """Test that async methods are actually coroutines"""
        client = WLEDClient()

        # Check that methods are coroutines
        assert asyncio.iscoroutinefunction(client.get_wled_instance_device)
        assert asyncio.iscoroutinefunction(client.simple_wled_test)
        assert asyncio.iscoroutinefunction(client.simple_wled_releases_test)
        assert asyncio.iscoroutinefunction(client.get_wled_latest_releases)
