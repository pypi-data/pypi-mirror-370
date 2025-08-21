"""
Test configuration and fixtures for MCP tools.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    files = {
        "test.txt": "This is a test file.",
        "data.json": '{"key": "value", "number": 42}',
        "code.py": "def hello():\n    return 'Hello, World!'",
        "README.md": "# Test Project\n\nThis is a test project."
    }
    
    created_files = {}
    for filename, content in files.items():
        file_path = temp_dir / filename
        file_path.write_text(content)
        created_files[filename] = file_path
    
    return created_files


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "status": "success",
        "data": {"result": "test data"},
        "timestamp": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "simple_task": "perform a simple operation",
        "complex_task": "analyze the project structure and generate a comprehensive report",
        "invalid_task": "",
        "edge_case_task": "handle this edge case with special characters: !@#$%^&*()",
        "long_task": "a" * 1000  # Very long task
    }


@pytest.fixture
def mock_kwargs():
    """Mock kwargs for testing."""
    return {
        "api_key": "test_api_key_12345",
        "timeout": 30,
        "max_results": 10,
        "format": "json"
    }


class ToolTestHelper:
    """Helper class for tool testing."""
    
    @staticmethod
    def assert_success_response(response: Dict[str, Any], expected_type: str = None):
        """Assert that response is a valid success response."""
        assert isinstance(response, dict), "Response must be a dictionary"
        assert response.get("success") is True, f"Expected success=True, got {response.get('success')}"
        assert "data" in response, "Success response must contain 'data'"
        assert "metadata" in response, "Success response must contain 'metadata'"
        
        metadata = response["metadata"]
        assert "tool_name" in metadata, "Metadata must contain 'tool_name'"
        assert "timestamp" in metadata, "Metadata must contain 'timestamp'"
        
        if expected_type:
            assert response.get("type") == expected_type, f"Expected type '{expected_type}', got '{response.get('type')}'"
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any], expected_error_code: str = None):
        """Assert that response is a valid error response."""
        assert isinstance(response, dict), "Response must be a dictionary"
        assert response.get("success") is False, f"Expected success=False, got {response.get('success')}"
        assert "error" in response, "Error response must contain 'error'"
        
        if expected_error_code:
            assert response.get("error_code") == expected_error_code, \
                f"Expected error_code '{expected_error_code}', got '{response.get('error_code')}'"
    
    @staticmethod
    def assert_stateless_behavior(tool, task: str, **kwargs):
        """Assert that tool behaves statelessly."""
        # Execute the same task multiple times
        results = []
        for _ in range(3):
            result = tool.execute(task, **kwargs)
            # Remove timestamp for comparison
            if "metadata" in result and "timestamp" in result["metadata"]:
                result = result.copy()
                result["metadata"] = result["metadata"].copy()
                del result["metadata"]["timestamp"]
            results.append(result)
        
        # All results should be identical
        for i in range(1, len(results)):
            assert results[0] == results[i], f"Tool is not stateless: result {i} differs from result 0"


@pytest.fixture
def tool_test_helper():
    """Provide tool test helper."""
    return ToolTestHelper()


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Clean up test environment
    test_vars = ["TESTING", "LOG_LEVEL"]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]


@pytest.fixture
def capture_logs(caplog):
    """Capture logs for testing."""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog
