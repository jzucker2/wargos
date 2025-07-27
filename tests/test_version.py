import unittest
from app.version import version


class TestVersion(unittest.TestCase):
    def test_version_is_string(self):
        """Test that version is a string"""
        self.assertIsInstance(version, str)

    def test_version_format(self):
        """Test that version follows semantic versioning format"""
        import re

        # Check if version follows semantic versioning (x.y.z)
        version_pattern = r"^\d+\.\d+\.\d+$"
        self.assertIsNotNone(
            re.match(version_pattern, version),
            f"Version {version} should follow semantic versioning format",
        )

    def test_version_not_empty(self):
        """Test that version is not empty"""
        self.assertGreater(len(version), 0)


if __name__ == "__main__":
    unittest.main()
