import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.scraper import Scraper


class TestPresetDownload:
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = TestClient(app)

        # Create test backup directory structure
        self.backup_dir = Path(self.temp_dir) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Create test device directory
        self.device_ip = "192.168.1.100"
        self.device_dir = self.backup_dir / self.device_ip / "presets"
        self.device_dir.mkdir(parents=True, exist_ok=True)

        # Create test backup files
        self.create_test_backup_files()

    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_backup_files(self):
        """Create test backup files with different timestamps"""
        test_presets = [
            {
                "timestamp": "20250728_110000",
                "presets": {
                    "1": {
                        "name": "Rainbow",
                        "segments": [{"id": 0, "start": 0, "stop": 60}],
                    }
                },
            },
            {
                "timestamp": "20250728_120000",
                "presets": {
                    "2": {
                        "name": "Solid",
                        "segments": [{"id": 0, "start": 0, "stop": 60}],
                    }
                },
            },
            {
                "timestamp": "20250728_130000",
                "presets": {
                    "3": {
                        "name": "Fade",
                        "segments": [{"id": 0, "start": 0, "stop": 60}],
                    }
                },
            },
        ]

        for i, test_preset in enumerate(test_presets):
            filename = (
                f"{self.device_ip}_{test_preset['timestamp']}_presets.json"
            )
            filepath = self.device_dir / filename

            # Add metadata to presets
            presets_data = test_preset["presets"].copy()
            presets_data["_backup_metadata"] = {
                "backup_timestamp": f"2025-07-28T{test_preset['timestamp'][:2]}:{test_preset['timestamp'][2:4]}:{test_preset['timestamp'][4:6]}.000000",
                "device_ip": self.device_ip,
                "backup_source": "wargos",
            }

            with open(filepath, "w") as f:
                json.dump(presets_data, f, indent=2)

            # Set different modification times to ensure proper sorting
            mtime = time.time() + i
            os.utime(filepath, (mtime, mtime))

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_presets_success(self, mock_backup_dir):
        """Test successful download of latest presets file (default: metadata stripped)"""
        mock_backup_dir.return_value = str(self.backup_dir)

        response = self.client.get(f"/presets/download/{self.device_ip}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{self.device_ip}_latest_presets.json"'
        )

        # Verify the content is the latest presets (should be Fade) and metadata is stripped
        content = response.json()
        assert "3" in content
        assert content["3"]["name"] == "Fade"
        assert "_backup_metadata" not in content

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_presets_with_metadata(self, mock_backup_dir):
        """Test successful download of latest presets file with metadata included"""
        mock_backup_dir.return_value = str(self.backup_dir)

        response = self.client.get(
            f"/presets/download/{self.device_ip}?include_metadata=true"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{self.device_ip}_latest_presets.json"'
        )

        # Verify the content is the latest presets (should be Fade) and metadata is included
        content = response.json()
        assert "3" in content
        assert content["3"]["name"] == "Fade"
        assert "_backup_metadata" in content
        assert content["_backup_metadata"]["device_ip"] == self.device_ip
        assert content["_backup_metadata"]["backup_source"] == "wargos"

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_presets_empty_presets(self, mock_backup_dir):
        """Test download when the latest presets file contains empty presets"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Create an empty presets file with later timestamp
        empty_filename = f"{self.device_ip}_20250728_140000_presets.json"
        empty_filepath = self.device_dir / empty_filename

        empty_presets_data = {"0": {}}

        with open(empty_filepath, "w") as f:
            json.dump(empty_presets_data, f, indent=2)

        # Set modification time to ensure this is the latest
        mtime = time.time() + 100
        os.utime(empty_filepath, (mtime, mtime))

        response = self.client.get(f"/presets/download/{self.device_ip}")

        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "empty_presets"
        assert content["device_ip"] == self.device_ip
        assert "No presets available" in content["message"]
        assert content["presets"] == {"0": {}}

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_presets_no_directory(self, mock_backup_dir):
        """Test download when no backup directory exists"""
        mock_backup_dir.return_value = str(self.backup_dir)

        response = self.client.get("/presets/download/192.168.1.999")

        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "not_found"
        assert "No presets backup directory found" in content["error"]

    @patch.object(Scraper, "get_config_backup_dir")
    def test_download_latest_presets_no_files(self, mock_backup_dir):
        """Test download when no backup files exist"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Create directory but no files
        empty_device_dir = self.backup_dir / "192.168.1.999" / "presets"
        empty_device_dir.mkdir(parents=True, exist_ok=True)

        response = self.client.get("/presets/download/192.168.1.999")

        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "not_found"
        assert "No presets backup files found" in content["error"]

    def test_presets_download_route_exists(self):
        """Test that the presets download route exists"""
        response = self.client.get("/presets/download/test_ip")
        # Should get a response (even if it's an error due to missing directory)
        assert response.status_code == 200

    @patch.object(Scraper, "get_config_backup_dir")
    def test_presets_download_metrics_tracking(self, mock_backup_dir):
        """Test that metrics are properly tracked for presets download operations"""
        mock_backup_dir.return_value = str(self.backup_dir)

        # Test successful download
        response = self.client.get(f"/presets/download/{self.device_ip}")
        assert response.status_code == 200

        # Test empty presets download
        empty_filename = f"{self.device_ip}_20250728_140000_presets.json"
        empty_filepath = self.device_dir / empty_filename
        empty_presets_data = {"0": {}}
        with open(empty_filepath, "w") as f:
            json.dump(empty_presets_data, f, indent=2)
        mtime = time.time() + 100
        os.utime(empty_filepath, (mtime, mtime))

        response = self.client.get(f"/presets/download/{self.device_ip}")
        assert response.status_code == 200
        content = response.json()
        assert content["status"] == "empty_presets"
