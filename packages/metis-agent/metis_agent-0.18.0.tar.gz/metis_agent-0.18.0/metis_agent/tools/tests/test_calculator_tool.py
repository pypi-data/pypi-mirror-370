"""
Test for CalculatorTool - Example of comprehensive tool testing.
"""

import pytest
from metis_agent.tools.core_tools.calculator_tool import CalculatorTool


class TestCalculatorTool:
    """Test suite for CalculatorTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = CalculatorTool()
    
    def test_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "Calculator"
        assert self.tool.description is not None
        assert len(self.tool.supported_operations) > 0
    
    def test_can_handle_valid_tasks(self):
        """Test that tool correctly identifies valid tasks."""
        valid_tasks = [
            "calculate 2 + 2",
            "what is 15 * 7", 
            "compute 100 / 4",
            "2 + 3 * 4",
            "math problem: 5 - 2"
        ]
        
        for task in valid_tasks:
            assert self.tool.can_handle(task), f"Should handle: {task}"
    
    def test_can_handle_invalid_tasks(self):
        """Test that tool correctly rejects invalid tasks."""
        invalid_tasks = [
            "write a poem",
            "search the web",
            "create a file",
            "",
            "   "
        ]
        
        for task in invalid_tasks:
            assert not self.tool.can_handle(task), f"Should not handle: {task}"
    
    def test_execute_simple_addition(self, tool_test_helper):
        """Test simple addition."""
        result = self.tool.execute("calculate 2 + 2")
        
        tool_test_helper.assert_success_response(result, "calculator_response")
        assert result["data"]["result"] == 4
        assert result["data"]["expression"] == "2 + 2"
    
    def test_execute_complex_expression(self, tool_test_helper):
        """Test complex mathematical expression."""
        result = self.tool.execute("calculate 2 + 3 * 4")
        
        tool_test_helper.assert_success_response(result)
        assert result["data"]["result"] == 14  # Order of operations
    
    def test_execute_division_by_zero(self, tool_test_helper):
        """Test division by zero error handling."""
        result = self.tool.execute("calculate 5 / 0")
        
        tool_test_helper.assert_error_response(result, "DIVISION_BY_ZERO")
    
    def test_execute_empty_task(self, tool_test_helper):
        """Test empty task handling."""
        result = self.tool.execute("")
        
        tool_test_helper.assert_error_response(result, "INVALID_INPUT")
    
    def test_execute_no_expression(self, tool_test_helper):
        """Test task with no mathematical expression."""
        result = self.tool.execute("hello world")
        
        tool_test_helper.assert_error_response(result, "NO_EXPRESSION")
    
    def test_stateless_behavior(self, tool_test_helper):
        """Test that tool is stateless."""
        task = "calculate 5 * 6"
        tool_test_helper.assert_stateless_behavior(self.tool, task)
    
    def test_get_examples(self):
        """Test that tool provides valid examples."""
        examples = self.tool.get_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # All examples should be handleable by the tool
        for example in examples:
            assert self.tool.can_handle(example)
    
    def test_expression_safety(self):
        """Test expression safety validation."""
        # Safe expressions
        safe_expressions = ["2 + 2", "10 * 5", "(3 + 4) / 2"]
        for expr in safe_expressions:
            assert self.tool._is_safe_expression(expr)
        
        # Unsafe expressions
        unsafe_expressions = ["__import__('os')", "exec('print(1)')", "import sys"]
        for expr in unsafe_expressions:
            assert not self.tool._is_safe_expression(expr)
