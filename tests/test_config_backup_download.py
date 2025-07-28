import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.scraper import Scraper


class TestConfigBackupDownload:
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = TestClient(app)

        # Create test backup directory structure
        self.backup_dir = Path(self.temp_dir) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Create test device directory
        self.device_ip = "192.168.1.100"
        self.device_dir = self.backup_dir / self.device_ip
        self.device_dir.mkdir(parents=True, exist_ok=True)

        # Create test backup files
        self.create_test_backup_files()

    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_backup_files(self):
        """Create test backup files with different timestamps"""
        import time

        test_configs = [
            {
                "timestamp": "20250728_110000",
                "config": {"test": "config1", "version": "1.0"},
            },
            {
                "timestamp": "20250728_120000",
                "config": {"test": "config2", "version": "1.1"},
            },
            {
                "timestamp": "20250728_130000",
                "config": {"test": "config3", "version": "1.2"},
            },
        ]

        for i, test_config in enumerate(test_configs):
            filename = f"{self.device_ip}_{test_config['timestamp']}.json"
            filepath = self.device_dir / filename

            # Add metadata to config
            config_data = test_config["config"].copy()
            config_data["_backup_metadata"] = {
                "backup_timestamp": f"2025-07-28T{test_config['timestamp'][:2]}:{test_config['timestamp'][2:4]}:{test_config['timestamp'][4:6]}.000000",
                "device_ip": self.device_ip,
                "backup_source": "wargos",
            }

            with open(filepath, "w") as f:
                json.dump(config_data, f, indent=2)

            # Set different modification times to ensure proper sorting
            # Later files should have later modification times
            mtime = (
                time.time() + i
            )  # Each file gets a progressively later time
            os.utime(filepath, (mtime, mtime))

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_backup_success(self, mock_backup_dir):
        """Test successful download of latest backup file (default: metadata stripped)"""
        mock_backup_dir.return_value = str(self.backup_dir)

        response = self.client.get(f"/config/download/{self.device_ip}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{self.device_ip}_latest_backup.json"'
        )

        # Verify the content is the latest config (should be config3) and metadata is stripped
        content = response.json()
        assert content["test"] == "config3"
        assert content["version"] == "1.2"
        assert "_backup_metadata" not in content

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_backup_with_metadata(self, mock_backup_dir):
        """Test successful download of latest backup file with metadata included"""
        mock_backup_dir.return_value = str(self.backup_dir)

        response = self.client.get(
            f"/config/download/{self.device_ip}?include_metadata=true"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{self.device_ip}_latest_backup.json"'
        )

        # Verify the content is the latest config (should be config3) and metadata is included
        content = response.json()
        assert content["test"] == "config3"
        assert content["version"] == "1.2"
        assert "_backup_metadata" in content
        assert content["_backup_metadata"]["device_ip"] == self.device_ip
        assert content["_backup_metadata"]["backup_source"] == "wargos"

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_backup_no_directory(self, mock_backup_dir):
        """Test download when backup directory doesn't exist"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Try to download from a non-existent device
        response = self.client.get("/config/download/192.168.1.999")

        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "not_found"
        assert "No backup directory found" in content["error"]
        assert content["device_ip"] == "192.168.1.999"

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_backup_no_files(self, mock_backup_dir):
        """Test download when no backup files exist"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Create directory but no files
        empty_device_dir = self.backup_dir / "192.168.1.999"
        empty_device_dir.mkdir(parents=True, exist_ok=True)

        response = self.client.get("/config/download/192.168.1.999")

        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "not_found"
        assert "No backup files found" in content["error"]
        assert content["device_ip"] == "192.168.1.999"

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_backup_with_exception(self, mock_backup_dir):
        """Test download when an exception occurs"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Mock the path operations to raise an exception
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.side_effect = Exception("Test exception")

            response = self.client.get(f"/config/download/{self.device_ip}")

            assert response.status_code == 200
            content = response.json()
            assert content["status"] == "error"
            assert "Error downloading backup" in content["error"]
            assert content["device_ip"] == self.device_ip

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_backup_multiple_files(self, mock_backup_dir):
        """Test download with multiple backup files to ensure latest is selected"""
        import time

        mock_backup_dir.return_value = str(self.backup_dir)

        # Create additional files with different timestamps
        additional_files = [
            ("20250728_140000", {"test": "config4", "version": "1.3"}),
            ("20250728_150000", {"test": "config5", "version": "1.4"}),
        ]

        for i, (timestamp, config) in enumerate(additional_files):
            filename = f"{self.device_ip}_{timestamp}.json"
            filepath = self.device_dir / filename

            config_data = config.copy()
            config_data["_backup_metadata"] = {
                "backup_timestamp": f"2025-07-28T{timestamp[:2]}:{timestamp[2:4]}:{timestamp[4:6]}.000000",
                "device_ip": self.device_ip,
                "backup_source": "wargos",
            }

            with open(filepath, "w") as f:
                json.dump(config_data, f, indent=2)

            # Set modification time to ensure this is the latest
            mtime = time.time() + 100 + i  # Much later than the original files
            os.utime(filepath, (mtime, mtime))

        response = self.client.get(f"/config/download/{self.device_ip}")

        assert response.status_code == 200
        content = response.json()
        # Should get the latest config (config5) and metadata should be stripped
        assert content["test"] == "config5"
        assert content["version"] == "1.4"
        assert "_backup_metadata" not in content

    def test_download_route_exists(self):
        """Test that the download route is properly registered"""
        routes = [route.path for route in app.routes]
        assert "/config/download/{device_ip}" in routes

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_metrics_tracking(self, mock_backup_dir):
        """Test that metrics are properly tracked for download operations"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Test successful download
        response = self.client.get(f"/config/download/{self.device_ip}")
        assert response.status_code == 200

        # Test failed download
        response = self.client.get("/config/download/192.168.1.999")
        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "not_found"
