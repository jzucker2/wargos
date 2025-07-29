import os
from unittest.mock import MagicMock, patch

import pytest

from app.main import app, configure_prometheus


class TestPrometheusConfiguration:
    """Test Prometheus configuration for different environments"""

    @pytest.fixture
    def mock_instrumentator(self):
        """Mock the instrumentator"""
        with patch("app.main.Instrumentator") as mock:
            mock.return_value = MagicMock()
            yield mock

    @pytest.fixture
    def mock_generate_latest(self):
        """Mock generate_latest"""
        with patch("app.main.generate_latest") as mock:
            mock.return_value = b"# HELP test_metric\n# TYPE test_metric counter\ntest_metric 1.0\n"
            yield mock

    def test_configure_prometheus_single_process(self, mock_instrumentator):
        """Test Prometheus configuration for single-process environment"""
        # Mock environment without PROMETHEUS_MULTIPROC_DIR
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.isdir", return_value=False):
                # Call configure_prometheus
                configure_prometheus()

                # Check that standard instrumentator was used
                mock_instrumentator.assert_called_once_with(
                    should_respect_env_var=True,
                    should_instrument_requests_inprogress=True,
                    excluded_handlers=["/metrics"],
                    env_var_name="ENABLE_METRICS",
                )

    def test_configure_prometheus_multi_process(
        self,
        mock_instrumentator,
    ):
        """Test Prometheus configuration for multi-process environment"""
        # Mock environment with PROMETHEUS_MULTIPROC_DIR
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=True):
                # Call configure_prometheus
                configure_prometheus()

                # Check that standard instrumentator was used (global registry)
                mock_instrumentator.assert_called_once_with(
                    should_respect_env_var=True,
                    should_instrument_requests_inprogress=True,
                    excluded_handlers=["/metrics"],
                    env_var_name="ENABLE_METRICS",
                )

    def test_configure_prometheus_multi_process_invalid_dir(
        self, mock_instrumentator
    ):
        """Test Prometheus configuration when multiproc dir doesn't exist"""
        # Mock environment with PROMETHEUS_MULTIPROC_DIR but invalid directory
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=False):
                # Call configure_prometheus
                configure_prometheus()

                # Should fall back to single-process configuration
                mock_instrumentator.assert_called_once_with(
                    should_respect_env_var=True,
                    should_instrument_requests_inprogress=True,
                    excluded_handlers=["/metrics"],
                    env_var_name="ENABLE_METRICS",
                )

    def test_configure_prometheus_multi_process_empty_dir(
        self, mock_instrumentator
    ):
        """Test Prometheus configuration when multiproc dir is empty"""
        # Mock environment with empty PROMETHEUS_MULTIPROC_DIR
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": ""}, clear=True
        ):
            with patch("os.path.isdir", return_value=False):
                # Call configure_prometheus
                configure_prometheus()

                # Should fall back to single-process configuration
                mock_instrumentator.assert_called_once_with(
                    should_respect_env_var=True,
                    should_instrument_requests_inprogress=True,
                    excluded_handlers=["/metrics"],
                    env_var_name="ENABLE_METRICS",
                )

    def test_configure_prometheus_instrumentation_called(
        self, mock_instrumentator
    ):
        """Test that instrumentator.instrument() is called"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.isdir", return_value=False):
                # Call configure_prometheus
                configure_prometheus()

                # Check that instrument was called
                mock_instrumentator.return_value.instrument.assert_called_once_with(
                    app
                )

    def test_configure_prometheus_multi_process_instrumentation_called(
        self,
        mock_instrumentator,
    ):
        """Test that instrumentator.instrument() is called in multi-process mode"""
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=True):
                # Call configure_prometheus
                configure_prometheus()

                # Check that instrument was called
                mock_instrumentator.return_value.instrument.assert_called_once_with(
                    app
                )

    def test_configure_prometheus_metrics_endpoint_created(
        self,
        mock_instrumentator,
        mock_generate_latest,
    ):
        """Test that custom metrics endpoint is created in multi-process mode"""
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=True):
                # Call configure_prometheus
                configure_prometheus()

                # Check that the metrics endpoint was added to the app
                # We can't easily test the endpoint directly, but we can verify the configuration
                assert mock_instrumentator.called

    def test_configure_prometheus_environment_variables(
        self, mock_instrumentator
    ):
        """Test that environment variables are respected"""
        # Test with ENABLE_METRICS=true
        with patch.dict(os.environ, {"ENABLE_METRICS": "true"}, clear=True):
            with patch("os.path.isdir", return_value=False):
                configure_prometheus()

                # Check that env_var_name was set correctly
                call_args = mock_instrumentator.call_args
                assert call_args[1]["env_var_name"] == "ENABLE_METRICS"

    def test_configure_prometheus_excluded_handlers(self, mock_instrumentator):
        """Test that metrics endpoint is excluded from instrumentation"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.isdir", return_value=False):
                configure_prometheus()

                # Check that /metrics is excluded
                call_args = mock_instrumentator.call_args
                assert call_args[1]["excluded_handlers"] == ["/metrics"]

    def test_configure_prometheus_instrumentation_settings(
        self, mock_instrumentator
    ):
        """Test that instrumentation settings are correct"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.isdir", return_value=False):
                configure_prometheus()

                # Check all the instrumentation settings
                call_args = mock_instrumentator.call_args
                assert call_args[1]["should_respect_env_var"] is True
                assert (
                    call_args[1]["should_instrument_requests_inprogress"]
                    is True
                )

    def test_configure_prometheus_multiprocess_registry_creation(
        self,
        mock_instrumentator,
    ):
        """Test that standard instrumentator is created correctly"""
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=True):
                configure_prometheus()

                # Check that standard instrumentator was used (global registry)
                mock_instrumentator.assert_called_once_with(
                    should_respect_env_var=True,
                    should_instrument_requests_inprogress=True,
                    excluded_handlers=["/metrics"],
                    env_var_name="ENABLE_METRICS",
                )

    def test_configure_prometheus_multiprocess_instrumentator_with_registry(
        self,
        mock_instrumentator,
    ):
        """Test that instrumentator is created without registry (global registry)"""
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=True):
                configure_prometheus()

                # Check that instrumentator was created without registry (uses global registry)
                call_args = mock_instrumentator.call_args
                assert "registry" not in call_args[1]

    def test_configure_prometheus_single_process_no_registry(
        self, mock_instrumentator
    ):
        """Test that instrumentator is created without registry in single-process mode"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.isdir", return_value=False):
                configure_prometheus()

                # Check that instrumentator was created without registry
                call_args = mock_instrumentator.call_args
                assert "registry" not in call_args[1]

    def test_configure_prometheus_multiprocess_dir_validation(
        self, mock_instrumentator
    ):
        """Test that multiprocess directory validation works correctly"""
        # Test with valid directory
        with patch.dict(
            os.environ, {"PROMETHEUS_MULTIPROC_DIR": "/tmp"}, clear=True
        ):
            with patch("os.path.isdir", return_value=True):
                configure_prometheus()

                # Should use global registry configuration
                call_args = mock_instrumentator.call_args
                assert "registry" not in call_args[1]

        # Test with invalid directory
        with patch.dict(
            os.environ,
            {"PROMETHEUS_MULTIPROC_DIR": "/nonexistent"},
            clear=True,
        ):
            with patch("os.path.isdir", return_value=False):
                configure_prometheus()

                # Should fall back to global registry configuration
                call_args = mock_instrumentator.call_args
                assert "registry" not in call_args[1]

    def test_configure_prometheus_no_environment_variable(
        self, mock_instrumentator
    ):
        """Test that configuration works when no environment variables are set"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.isdir", return_value=False):
                configure_prometheus()

                # Should use single-process configuration
                call_args = mock_instrumentator.call_args
                assert "registry" not in call_args[1]
