"""
Test template for MCP tools.

Copy this file and rename it to test_your_tool.py.
Replace TemplateTool with your actual tool class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from metis_agent.tools.TOOL_TEMPLATE import TemplateTool  # Replace with your tool import


class TestTemplateTool:
    """Test suite for TemplateTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = TemplateTool()
    
    def test_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "Template Tool"  # Replace with expected name
        assert self.tool.description is not None
        assert hasattr(self.tool, 'supported_formats')
        assert hasattr(self.tool, 'max_input_length')
    
    def test_can_handle_valid_tasks(self):
        """Test that tool correctly identifies valid tasks."""
        valid_tasks = [
            "template example task",
            "test the template functionality",
            "example of template usage"
        ]
        
        for task in valid_tasks:
            assert self.tool.can_handle(task), f"Should handle: {task}"
    
    def test_can_handle_invalid_tasks(self):
        """Test that tool correctly rejects invalid tasks."""
        invalid_tasks = [
            "completely unrelated task",
            "generate code for python",
            "search the web for information",
            "",  # Empty task
            "   ",  # Whitespace only
        ]
        
        for task in invalid_tasks:
            assert not self.tool.can_handle(task), f"Should not handle: {task}"
    
    def test_execute_success(self, tool_test_helper):
        """Test successful execution."""
        task = "template example task"
        result = self.tool.execute(task)
        
        tool_test_helper.assert_success_response(result, "templatetool_response")
        
        # Check specific data structure
        assert "processed_task" in result["data"]
        assert "task_length" in result["data"]
        assert "word_count" in result["data"]
        assert result["data"]["processed_task"] == task
    
    def test_execute_with_kwargs(self, tool_test_helper):
        """Test execution with additional parameters."""
        task = "template example task"
        kwargs = {
            "format": "json",
            "api_key": "test_key_123"
        }
        
        result = self.tool.execute(task, **kwargs)
        
        tool_test_helper.assert_success_response(result)
        assert result["metadata"]["format"] == "json"
        assert "parameters" in result["data"]
    
    def test_execute_empty_task(self, tool_test_helper):
        """Test execution with empty task."""
        result = self.tool.execute("")
        
        tool_test_helper.assert_error_response(result, "INVALID_INPUT")
        assert "empty" in result["error"].lower()
    
    def test_execute_whitespace_task(self, tool_test_helper):
        """Test execution with whitespace-only task."""
        result = self.tool.execute("   ")
        
        tool_test_helper.assert_error_response(result, "INVALID_INPUT")
    
    def test_execute_long_task(self, tool_test_helper):
        """Test execution with overly long task."""
        long_task = "a" * (self.tool.max_input_length + 1)
        result = self.tool.execute(long_task)
        
        tool_test_helper.assert_error_response(result, "INPUT_TOO_LONG")
    
    def test_execute_invalid_format(self, tool_test_helper):
        """Test execution with invalid format."""
        task = "template example task"
        result = self.tool.execute(task, format="invalid_format")
        
        tool_test_helper.assert_error_response(result, "INVALID_FORMAT")
        assert "Unsupported format" in result["error"]
    
    def test_stateless_behavior(self, tool_test_helper):
        """Test that tool is stateless."""
        task = "template example task"
        tool_test_helper.assert_stateless_behavior(self.tool, task)
    
    def test_get_examples(self):
        """Test that tool provides valid examples."""
        examples = self.tool.get_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # All examples should be handleable by the tool
        for example in examples:
            assert isinstance(example, str)
            assert len(example) > 0
            assert self.tool.can_handle(example), f"Tool should handle its own example: {example}"
    
    def test_api_key_extraction(self):
        """Test API key extraction from kwargs and environment."""
        # Test kwargs extraction
        kwargs = {"api_key": "test_key_123"}
        api_key = self.tool._get_api_key(kwargs)
        assert api_key == "test_key_123"
        
        # Test multiple key names
        kwargs = {"custom_key": "custom_value"}
        api_key = self.tool._get_api_key(kwargs, ["api_key", "custom_key"])
        assert api_key == "custom_value"
        
        # Test no key found
        kwargs = {}
        api_key = self.tool._get_api_key(kwargs)
        assert api_key is None
    
    @patch.dict('os.environ', {'API_KEY': 'env_key_456'})
    def test_api_key_from_environment(self):
        """Test API key extraction from environment."""
        kwargs = {}
        api_key = self.tool._get_api_key(kwargs)
        assert api_key == "env_key_456"
    
    def test_error_handling(self, tool_test_helper):
        """Test error handling in edge cases."""
        # Test with None task (should be handled gracefully)
        with pytest.raises(TypeError):
            self.tool.execute(None)
    
    def test_response_format_consistency(self):
        """Test that all responses follow the expected format."""
        # Success response
        success_result = self.tool.execute("template example task")
        assert "success" in success_result
        assert "metadata" in success_result
        assert "timestamp" in success_result["metadata"]
        assert "tool_name" in success_result["metadata"]
        
        # Error response
        error_result = self.tool.execute("")
        assert "success" in error_result
        assert "error" in error_result
        assert "error_code" in error_result
        assert "metadata" in error_result
    
    def test_concurrent_execution(self, tool_test_helper):
        """Test that tool handles concurrent execution properly."""
        import threading
        import time
        
        results = []
        errors = []
        
        def execute_task(task_id):
            try:
                result = self.tool.execute(f"template task {task_id}")
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=execute_task, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred during concurrent execution: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        # All results should be successful
        for result in results:
            tool_test_helper.assert_success_response(result)
    
    def test_memory_usage(self):
        """Test that tool doesn't leak memory."""
        import gc
        
        # Get initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Execute many operations
        for i in range(100):
            result = self.tool.execute(f"template task {i}")
            assert result["success"] is True
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count shouldn't grow significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 50, f"Potential memory leak: {object_growth} new objects"


# Integration tests
class TestTemplateToolIntegration:
    """Integration tests for TemplateTool."""
    
    def test_mcp_server_integration(self):
        """Test tool integration with MCP server."""
        # This test would verify that the tool is properly registered
        # and discoverable by the MCP server
        pass
    
    def test_tool_registry_integration(self):
        """Test tool integration with tool registry."""
        from tools import get_available_tools
        
        tools = get_available_tools()
        tool_names = [tool.__name__ for tool in tools]
        
        # Tool should be in the registry
        assert "TemplateTool" in tool_names
    
    def test_performance_benchmarks(self):
        """Test tool performance benchmarks."""
        import time
        
        task = "template performance test task"
        
        # Measure execution time
        start_time = time.time()
        result = self.tool.execute(task)
        execution_time = time.time() - start_time
        
        # Tool should execute quickly (adjust threshold as needed)
        assert execution_time < 1.0, f"Tool took too long to execute: {execution_time}s"
        assert result["success"] is True
