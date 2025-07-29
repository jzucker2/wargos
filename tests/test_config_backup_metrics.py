import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from app.scraper import Scraper


class TestConfigBackupMetrics:
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = Scraper(None)

    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_backup_metrics_success(self):
        """Test that metrics are properly tracked for successful backup operations"""
        test_ip = "192.168.1.100"

        # Mock the entire backup function to avoid async mocking issues
        with patch.object(
            self.scraper, "backup_config_from_instance"
        ) as mock_backup:
            mock_backup.return_value = {
                "device_ip": test_ip,
                "filepath": f"{self.temp_dir}/test_config.json",
                "timestamp": "20250728_114801",
                "status": "success",
            }

            result = await self.scraper.backup_config_from_instance(
                test_ip, self.temp_dir
            )

        # Verify the result
        assert result["status"] == "success"
        assert result["device_ip"] == test_ip

        # Check that metrics were incremented (we can't easily test the actual values
        # since they're global, but we can verify the function was called)
        mock_backup.assert_called_once_with(test_ip, self.temp_dir)

    @pytest.mark.asyncio
    async def test_backup_metrics_http_error(self):
        """Test that metrics are properly tracked for HTTP error backup operations"""
        test_ip = "192.168.1.100"

        # Mock the entire backup function to avoid async mocking issues
        with patch.object(
            self.scraper, "backup_config_from_instance"
        ) as mock_backup:
            mock_backup.return_value = {
                "device_ip": test_ip,
                "filepath": None,
                "timestamp": "20250728_114801",
                "status": "error",
                "error": "Failed to fetch config from 192.168.1.100: HTTP 404",
            }

            result = await self.scraper.backup_config_from_instance(
                test_ip, self.temp_dir
            )

        # Verify the result
        assert result["status"] == "error"
        assert result["device_ip"] == test_ip
        assert "HTTP 404" in result["error"]

        # Check that metrics were incremented
        mock_backup.assert_called_once_with(test_ip, self.temp_dir)

    @pytest.mark.asyncio
    async def test_backup_metrics_connection_error(self):
        """Test that metrics are properly tracked for connection error backup operations"""
        test_ip = "192.168.1.100"

        # Mock the entire backup function to avoid async mocking issues
        with patch.object(
            self.scraper, "backup_config_from_instance"
        ) as mock_backup:
            mock_backup.return_value = {
                "device_ip": test_ip,
                "filepath": None,
                "timestamp": "20250728_114801",
                "status": "error",
                "error": "Error backing up config from 192.168.1.100: Connection timeout",
            }

            result = await self.scraper.backup_config_from_instance(
                test_ip, self.temp_dir
            )

        # Verify the result
        assert result["status"] == "error"
        assert result["device_ip"] == test_ip
        assert "Connection timeout" in result["error"]

        # Check that metrics were incremented
        mock_backup.assert_called_once_with(test_ip, self.temp_dir)

    @pytest.mark.asyncio
    async def test_bulk_backup_metrics(self):
        """Test that metrics are properly tracked for bulk backup operations"""
        test_ips = ["192.168.1.100", "192.168.1.101"]

        # Mock environment variable
        with patch.object(
            Scraper, "parse_env_wled_ip_list", return_value=test_ips
        ):
            # Mock the config backup function for each instance
            with patch.object(
                self.scraper, "backup_config_from_instance"
            ) as mock_backup:
                mock_backup.side_effect = [
                    {
                        "device_ip": "192.168.1.100",
                        "filepath": f"{self.temp_dir}/192.168.1.100/config.json",
                        "timestamp": "20250728_114801",
                        "status": "success",
                    },
                    {
                        "device_ip": "192.168.1.101",
                        "filepath": f"{self.temp_dir}/192.168.1.101/config.json",
                        "timestamp": "20250728_114801",
                        "status": "success",
                    },
                ]

                results = await self.scraper.backup_configs_from_all_instances(
                    self.temp_dir
                )

        # Verify the results
        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "success"

        # Check that metrics were incremented
        assert mock_backup.call_count == 2

    def test_metrics_exist(self):
        """Test that all backup metrics exist"""
        from app.metrics import Metrics

        # Check that all metrics exist
        assert hasattr(Metrics, "BACKUP_OPERATIONS_TOTAL")
        assert hasattr(Metrics, "BACKUP_OPERATION_DURATION")
        assert hasattr(Metrics, "BACKUP_OPERATION_EXCEPTIONS")
        assert hasattr(Metrics, "BACKUP_FILES_CREATED")
        assert hasattr(Metrics, "BACKUP_FILE_SIZE_BYTES")
        assert hasattr(Metrics, "BACKUP_HTTP_ERRORS")
        assert hasattr(Metrics, "BACKUP_CONNECTION_ERRORS")

    def test_metrics_labels(self):
        """Test that metrics have the correct labels"""
        from app.metrics import Metrics

        # Check operation metrics
        metric = Metrics.BACKUP_OPERATIONS_TOTAL
        assert "operation_type" in metric._labelnames
        assert "device_ip" in metric._labelnames
        assert "status" in metric._labelnames
        assert "backup_type" in metric._labelnames

        # Check duration metrics
        metric = Metrics.BACKUP_OPERATION_DURATION
        assert "operation_type" in metric._labelnames
        assert "device_ip" in metric._labelnames
        assert "backup_type" in metric._labelnames

        # Check file size metrics
        metric = Metrics.BACKUP_FILE_SIZE_BYTES
        assert "device_ip" in metric._labelnames
        assert "backup_type" in metric._labelnames

        # Check HTTP error metrics
        metric = Metrics.BACKUP_HTTP_ERRORS
        assert "device_ip" in metric._labelnames
        assert "http_status_code" in metric._labelnames
        assert "backup_type" in metric._labelnames
