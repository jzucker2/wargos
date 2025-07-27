#!/usr/bin/env python3
"""
Test runner for the wargos application.
This script can run all tests or specific test modules.
"""

import sys
import unittest
import os
from pathlib import Path


def run_all_tests():
    """Run all tests in the tests directory"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Add the current directory to the path so we can import app modules
    sys.path.insert(0, str(project_root))

    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_test(test_module):
    """Run a specific test module"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Add the current directory to the path so we can import app modules
    sys.path.insert(0, str(project_root))

    # Import and run the specific test module
    try:
        module = __import__(f"tests.{test_module}", fromlist=["*"])
        suite = unittest.TestLoader().loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing test module {test_module}: {e}")
        return False


def main():
    """Main function to run tests"""
    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1]
        if not test_module.startswith("test_"):
            test_module = f"test_{test_module}"
        success = run_specific_test(test_module)
    else:
        # Run all tests
        print("Running all tests...")
        success = run_all_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
