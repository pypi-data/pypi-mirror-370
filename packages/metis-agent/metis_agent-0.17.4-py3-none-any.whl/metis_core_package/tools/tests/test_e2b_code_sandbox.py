"""
Unit tests for E2BCodeSandboxTool following TOOLS_RULES.MD testing requirements.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from metis_agent.tools.advanced_tools.e2b_code_sandbox import E2BCodeSandboxTool


class TestE2BCodeSandboxTool:
    """Test suite for E2BCodeSandboxTool with enhanced features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = E2BCodeSandboxTool()
        self.sample_api_key = "e2b_test_key_123"
        self.sample_code = "print('Hello, World!')"
    
    def test_initialization(self):
        """Test tool initialization and required attributes."""
        assert self.tool.name == "E2BCodeSandboxTool"
        assert self.tool.description is not None
        assert self.tool.version == "1.0.0"
        assert self.tool.category == "advanced_tools"
        assert isinstance(self.tool.code_patterns, list)
        assert isinstance(self.tool.supported_languages, list)
        assert self.tool.default_timeout == 30
        assert self.tool.max_timeout == 300
    
    def test_can_handle_valid_tasks(self):
        """Test can_handle method with valid code execution tasks."""
        valid_tasks = [
            "execute python code: print('hello')",
            "run this code in sandbox",
            "Execute this Python code: import numpy as np",
            "```python\nprint('test')\n```",
            "analyze data using pandas",
            "create matplotlib chart",
            "python script execution",
            "run machine learning model",
            "data visualization with seaborn"
        ]
        
        for task in valid_tasks:
            assert self.tool.can_handle(task), f"Should handle: {task}"
    
    def test_can_handle_invalid_tasks(self):
        """Test can_handle method with invalid tasks."""
        invalid_tasks = [
            "",
            None,
            "just regular text",
            "search the web",
            "send an email",
            "create a file",
            "what is the weather"
        ]
        
        for task in invalid_tasks:
            assert not self.tool.can_handle(task), f"Should not handle: {task}"
    
    def test_execute_empty_task(self):
        """Test execute with empty task."""
        result = self.tool.execute("")
        
        assert result["success"] is False
        assert result["error_code"] == "INVALID_INPUT"
        assert "Task cannot be empty" in result["error"]
        assert "performance" in result
    
    def test_execute_missing_api_key(self):
        """Test execute without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('metis_agent.auth.api_key_manager.APIKeyManager') as mock_manager:
                mock_manager.return_value.get_key.return_value = None
                
                result = self.tool.execute("print('test')")
                
                assert result["success"] is False
                assert result["error_code"] == "MISSING_API_KEY"
                assert "E2B API key is required" in result["error"]
    
    def test_execute_no_code_found(self):
        """Test execute when no code can be extracted."""
        result = self.tool.execute("just some text", e2b_api_key=self.sample_api_key)
        
        assert result["success"] is False
        assert result["error_code"] == "NO_CODE_FOUND"
        assert "No Python code found" in result["error"]
    
    @patch('e2b_code_interpreter.Sandbox')
    def test_execute_successful_code_execution(self, mock_sandbox_class):
        """Test successful code execution."""
        # Mock sandbox execution
        mock_sandbox = Mock()
        mock_execution = Mock()
        mock_execution.error = None
        mock_execution.logs = Mock()
        mock_execution.logs.stdout = "Hello, World!"
        mock_execution.logs.stderr = ""
        mock_execution.results = []
        
        mock_sandbox.run_code.return_value = mock_execution
        mock_sandbox_class.return_value = mock_sandbox
        
        result = self.tool.execute(
            "execute this code: print('Hello, World!')",
            e2b_api_key=self.sample_api_key
        )
        
        assert result["success"] is True
        assert result["type"] == "e2b_code_execution_response"
        assert "data" in result
        assert result["data"]["stdout"] == "Hello, World!"
        assert result["data"]["code"] == "print('Hello, World!')"
        assert "performance" in result
        assert result["performance"]["tool_name"] == "E2BCodeSandboxTool"
    
    @patch('e2b_code_interpreter.Sandbox')
    def test_execute_with_error(self, mock_sandbox_class):
        """Test code execution with error."""
        # Mock sandbox execution with error
        mock_sandbox = Mock()
        mock_execution = Mock()
        mock_execution.error = "NameError: name 'undefined_var' is not defined"
        mock_execution.logs = Mock()
        mock_execution.logs.stdout = ""
        mock_execution.logs.stderr = "NameError: name 'undefined_var' is not defined"
        mock_execution.results = []
        
        mock_sandbox.run_code.return_value = mock_execution
        mock_sandbox_class.return_value = mock_sandbox
        
        result = self.tool.execute(
            "print(undefined_var)",
            e2b_api_key=self.sample_api_key
        )
        
        assert result["success"] is True  # Execution succeeded, but code had error
        assert result["data"]["error"] is not None
        assert result["data"]["execution_status"] == "error"
    
    def test_extract_code_from_code_blocks(self):
        """Test code extraction from markdown code blocks."""
        test_cases = [
            ("```python\nprint('hello')\n```", "print('hello')"),
            ("```py\nimport os\nprint(os.getcwd())\n```", "import os\nprint(os.getcwd())"),
            ("Execute this:\n```python\nx = 5\nprint(x)\n```", "x = 5\nprint(x)"),
        ]
        
        for task, expected_code in test_cases:
            extracted = self.tool._extract_code(task)
            assert extracted == expected_code, f"Failed for: {task}"
    
    def test_extract_code_explicit(self):
        """Test explicit code parameter takes precedence."""
        task = "some task description"
        explicit_code = "print('explicit')"
        
        extracted = self.tool._extract_code(task, explicit_code)
        assert extracted == explicit_code
    
    def test_looks_like_code_detection(self):
        """Test heuristic code detection."""
        code_samples = [
            "import numpy as np\nprint(np.array([1,2,3]))",
            "def hello():\n    return 'world'",
            "for i in range(10):\n    print(i)",
            "x = 5\nif x > 0:\n    print('positive')"
        ]
        
        non_code_samples = [
            "just regular text",
            "hello world",
            "this is a sentence"
        ]
        
        for code in code_samples:
            assert self.tool._looks_like_code(code), f"Should detect as code: {code}"
        
        for text in non_code_samples:
            assert not self.tool._looks_like_code(text), f"Should not detect as code: {text}"
    
    def test_get_api_key_priority(self):
        """Test API key retrieval priority."""
        kwargs = {"e2b_api_key": "kwargs_key"}
        
        # Test kwargs priority
        api_key = self.tool._get_api_key(kwargs)
        assert api_key == "kwargs_key"
        
        # Test environment variable fallback
        with patch.dict(os.environ, {"E2B_API_KEY": "env_key"}):
            api_key = self.tool._get_api_key({})
            assert api_key == "env_key"
    
    def test_get_capabilities(self):
        """Test capability metadata structure."""
        capabilities = self.tool.get_capabilities()
        
        required_keys = [
            "complexity_levels", "input_types", "output_types",
            "estimated_execution_time", "requires_internet",
            "requires_filesystem", "concurrent_safe",
            "resource_intensive", "supported_intents",
            "api_dependencies", "memory_usage"
        ]
        
        for key in required_keys:
            assert key in capabilities, f"Missing capability key: {key}"
        
        assert "e2b" in capabilities["api_dependencies"]
        assert capabilities["requires_internet"] is True
        assert capabilities["resource_intensive"] is True
    
    def test_get_examples(self):
        """Test example tasks."""
        examples = self.tool.get_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # All examples should be handleable by the tool
        for example in examples:
            assert self.tool.can_handle(example), f"Tool should handle its own example: {example}"
    
    def test_stateless_behavior(self):
        """Test that tool maintains no state between calls."""
        task = "print('test')"
        
        with patch('e2b_code_interpreter.Sandbox') as mock_sandbox_class:
            mock_sandbox = Mock()
            mock_execution = Mock()
            mock_execution.error = None
            mock_execution.logs = Mock()
            mock_execution.logs.stdout = "test"
            mock_execution.logs.stderr = ""
            mock_execution.results = []
            
            mock_sandbox.run_code.return_value = mock_execution
            mock_sandbox_class.return_value = mock_sandbox
            
            result1 = self.tool.execute(task, e2b_api_key=self.sample_api_key)
            result2 = self.tool.execute(task, e2b_api_key=self.sample_api_key)
            
            # Results should be identical (excluding timestamps)
            assert result1["success"] == result2["success"]
            assert result1["data"]["code"] == result2["data"]["code"]
            assert result1["data"]["stdout"] == result2["data"]["stdout"]
    
    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        with patch('e2b_code_interpreter.Sandbox') as mock_sandbox_class:
            mock_sandbox = Mock()
            mock_execution = Mock()
            mock_execution.error = None
            mock_execution.logs = Mock()
            mock_execution.logs.stdout = "test"
            mock_execution.logs.stderr = ""
            mock_execution.results = []
            
            mock_sandbox.run_code.return_value = mock_execution
            mock_sandbox_class.return_value = mock_sandbox
            
            result = self.tool.execute("print('test')", e2b_api_key=self.sample_api_key)
            
            assert "performance" in result
            performance = result["performance"]
            
            assert "execution_time" in performance
            assert "memory_usage_mb" in performance
            assert "api_calls_made" in performance
            assert "tool_name" in performance
            assert performance["tool_name"] == "E2BCodeSandboxTool"
            assert isinstance(performance["execution_time"], (int, float))
    
    def test_error_response_structure(self):
        """Test error response follows TOOLS_RULES.MD format."""
        result = self.tool.execute("")  # Empty task to trigger error
        
        required_error_keys = [
            "success", "error", "error_code", "error_type",
            "details", "suggestions", "metadata", "performance"
        ]
        
        for key in required_error_keys:
            assert key in result, f"Missing error response key: {key}"
        
        assert result["success"] is False
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0
        assert result["metadata"]["tool_name"] == "E2BCodeSandboxTool"
    
    @patch('e2b_code_interpreter.Sandbox')
    def test_package_installation(self, mock_sandbox_class):
        """Test package installation functionality."""
        mock_sandbox = Mock()
        mock_execution = Mock()
        mock_execution.error = None
        mock_execution.logs = Mock()
        mock_execution.logs.stdout = "Package installed successfully"
        mock_execution.logs.stderr = ""
        mock_execution.results = []
        
        mock_sandbox.run_code.return_value = mock_execution
        mock_sandbox_class.return_value = mock_sandbox
        
        result = self.tool.execute(
            "import pandas as pd",
            e2b_api_key=self.sample_api_key,
            install_packages=["pandas"]
        )
        
        assert result["success"] is True
        assert result["metadata"]["packages_installed"] == 1
        
        # Verify pip install was called
        calls = mock_sandbox.run_code.call_args_list
        install_calls = [call for call in calls if "pip install" in str(call)]
        assert len(install_calls) > 0
    
    @patch('e2b_code_interpreter.Sandbox')
    def test_file_operations(self, mock_sandbox_class):
        """Test file creation in sandbox."""
        mock_sandbox = Mock()
        mock_execution = Mock()
        mock_execution.error = None
        mock_execution.logs.stdout = "File operations completed"
        mock_execution.logs.stderr = ""
        mock_execution.results = []
        
        mock_sandbox.run_code.return_value = mock_execution
        mock_sandbox_class.return_value = mock_sandbox
        
        files = {
            "data.txt": "sample data",
            "config.json": '{"key": "value"}'
        }
        
        result = self.tool.execute(
            "print('Files created')",
            e2b_api_key=self.sample_api_key,
            files=files
        )
        
        assert result["success"] is True
        assert len(result["data"]["files_created"]) == 2
        
        # Verify files.write was called
        assert mock_sandbox.files.write.call_count == 2
    
    def test_timeout_parameter(self):
        """Test timeout parameter handling."""
        # Test default timeout
        assert self.tool.default_timeout == 30
        
        # Test max timeout enforcement
        with patch('e2b_code_interpreter.Sandbox') as mock_sandbox_class:
            mock_sandbox = Mock()
            mock_execution = Mock()
            mock_execution.error = None
            mock_execution.logs = Mock()
            mock_execution.logs.stdout = "test"
            mock_execution.logs.stderr = ""
            mock_execution.results = []
            
            mock_sandbox.run_code.return_value = mock_execution
            mock_sandbox_class.return_value = mock_sandbox
            
            # Request timeout higher than max
            result = self.tool.execute(
                "print('test')",
                e2b_api_key=self.sample_api_key,
                timeout=500  # Higher than max_timeout (300)
            )
            
            assert result["success"] is True
            assert result["metadata"]["timeout_used"] == 300  # Should be capped at max
    
    def test_cleanup_sandboxes(self):
        """Test sandbox cleanup functionality."""
        # Add mock sandboxes
        mock_sandbox1 = Mock()
        mock_sandbox2 = Mock()
        
        self.tool.active_sandboxes = {
            "sandbox_1": mock_sandbox1,
            "sandbox_2": mock_sandbox2
        }
        
        self.tool.cleanup_sandboxes()
        
        # Verify close was called on all sandboxes
        mock_sandbox1.close.assert_called_once()
        mock_sandbox2.close.assert_called_once()
        
        # Verify sandboxes were cleared
        assert len(self.tool.active_sandboxes) == 0
    
    def test_sdk_import_error_handling(self):
        """Test handling of missing E2B SDK."""
        # Create a new tool instance to avoid cached imports
        from metis_agent.tools.advanced_tools.e2b_code_sandbox import E2BCodeSandboxTool
        
        # Mock the import inside _execute_in_sandbox to raise ImportError
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                if name == 'e2b_code_interpreter':
                    raise ImportError("No module named 'e2b_code_interpreter'")
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            tool = E2BCodeSandboxTool()
            result = tool.execute(
                "print('test')",
                e2b_api_key=self.sample_api_key
            )
            
            assert result["success"] is True  # Tool execution succeeds
            assert "E2B SDK not installed" in result["data"]["error"]
            assert result["data"]["execution_status"] == "failed"


if __name__ == "__main__":
    pytest.main([__file__])
