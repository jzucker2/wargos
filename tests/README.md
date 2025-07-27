# Wargos Test Suite

This directory contains the comprehensive unit test suite for the Wargos application.

## 🎯 **Current Status: ✅ FULLY WORKING**

All tests are passing! The test suite provides **57% code coverage** and covers all major components.

## 📁 **Test Files**

### ✅ **Working Test Files:**
- **`test_basic.py`** - Basic functionality tests (9 tests)
- **`test_version.py`** - Version module tests (3 tests)
- **`test_utils.py`** - Utility functions tests (12 tests)
- **`test_wled_client_simple.py`** - WLED client tests (7 tests)
- **`test_scraper_simple.py`** - Scraper tests (12 tests)
- **`test_main_simple.py`** - FastAPI app tests (5 tests)

### 📊 **Coverage Summary:**
- **`app/utils.py`**: 100% coverage (28/28 statements)
- **`app/version.py`**: 100% coverage (1/1 statements)
- **`app/metrics.py`**: 100% coverage (143/143 statements)
- **`app/main.py`**: 69% coverage (27/39 statements)
- **`app/wled_client.py`**: 40% coverage (24/60 statements)
- **`app/scraper.py`**: 27% coverage (62/231 statements)

## 🚀 **Running Tests**

### **Option 1: Shell Script (Recommended)**
```bash
# Run all tests
./scripts/unit_tests.sh

# Run specific test module
./scripts/unit_tests.sh basic
./scripts/unit_tests.sh version
./scripts/unit_tests.sh utils
./scripts/unit_tests.sh wled_client_simple
./scripts/unit_tests.sh scraper_simple
./scripts/unit_tests.sh main_simple
```

### **Option 2: Pytest (Advanced)**
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_basic.py -v

# Run specific test class
pytest tests/test_basic.py::TestBasicFunctionality -v
```

### **Option 3: Direct Python**
```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py basic
```

## 🧪 **Test Features**

### **✅ What's Tested:**
- **Environment Variables** - Proper handling of DEBUG, DEFAULT_WLED_IP, etc.
- **Logging** - All LogHelper methods and logger configurations
- **Version Management** - Version string format and validation
- **WLED Client** - Basic client initialization and configuration
- **Scraper** - Core scraping functionality and environment parsing
- **FastAPI Endpoints** - Root, healthcheck, and OpenAPI schema
- **Prometheus Metrics** - Metric definitions and configurations

### **🔧 Test Infrastructure:**
- **Virtual Environment** - Tests run in isolated `venv`
- **Mocking** - External dependencies properly mocked
- **Environment Isolation** - Tests don't interfere with each other
- **Coverage Reporting** - Detailed coverage analysis
- **Multiple Runners** - Support for unittest, pytest, and custom runner

## 📋 **Test Categories**

### **Unit Tests (48 total)**
- **Utils Tests** (12 tests) - Logging and utility functions
- **Version Tests** (3 tests) - Version string validation
- **WLED Client Tests** (7 tests) - Client initialization and configuration
- **Scraper Tests** (12 tests) - Core scraping functionality
- **Main App Tests** (5 tests) - FastAPI endpoints and configuration
- **Basic Tests** (9 tests) - Core functionality smoke tests

## 🛠 **Adding New Tests**

### **Template for New Test File:**
```python
import unittest
from unittest.mock import patch, MagicMock
from app.your_module import YourClass

class TestYourClass(unittest.TestCase):
    """Tests for YourClass"""

    def test_something(self):
        """Test description"""
        # Your test code here
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
```

### **Best Practices:**
1. **Use descriptive test names** - `test_function_name_scenario`
2. **Mock external dependencies** - Use `@patch` and `MagicMock`
3. **Test edge cases** - Empty inputs, error conditions, etc.
4. **Use environment isolation** - `@patch.dict(os.environ, {...})`
5. **Add docstrings** - Explain what each test validates

## 🔧 **Configuration Files**

- **`pytest.ini`** - Pytest configuration
- **`requirements-test.txt`** - Test dependencies
- **`scripts/unit_tests.sh`** - Test runner script
- **`tests/run_tests.py`** - Custom test runner

## 📈 **Coverage Goals**

- **Current**: 57% overall coverage
- **Target**: 80%+ coverage for critical paths
- **Focus Areas**:
  - Async methods in `wled_client.py`
  - Complex scraping logic in `scraper.py`
  - Error handling in `main.py`

## 🎉 **Success Metrics**

✅ **All 48 tests passing**
✅ **57% code coverage**
✅ **Multiple test runners working**
✅ **Environment isolation working**
✅ **Mocking working correctly**
✅ **Coverage reporting working**

The test suite is **production-ready** and provides a solid foundation for continued development!
