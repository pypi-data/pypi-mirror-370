"""
Tests for enhanced base tool functionality.

Tests the new capabilities including performance monitoring,
query analysis, and tool composition features.
"""

import pytest
import time
from metis_agent.tools.base import BaseTool, ComposableTool, QueryAnalysis
from metis_agent.tools.core_tools.calculator_tool import CalculatorTool


class TestBaseTool:
    """Test suite for enhanced BaseTool functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = CalculatorTool()
    
    def test_get_capabilities(self):
        """Test that tools return capability metadata."""
        capabilities = self.calculator.get_capabilities()
        
        # Check required capability fields
        required_fields = [
            "complexity_levels", "input_types", "output_types",
            "requires_internet", "requires_filesystem", "concurrent_safe"
        ]
        
        for field in required_fields:
            assert field in capabilities, f"Missing capability field: {field}"
        
        # Validate specific values
        assert isinstance(capabilities["complexity_levels"], list)
        assert isinstance(capabilities["input_types"], list)
        assert isinstance(capabilities["requires_internet"], bool)
    
    def test_analyze_compatibility(self):
        """Test query analysis compatibility scoring."""
        # Test high compatibility query
        high_compat_query = QueryAnalysis(
            complexity="simple",
            intents=["calculate", "math"],
            requirements={"requires_internet": False},
            confidence=0.9
        )
        
        score = self.calculator.analyze_compatibility(high_compat_query)
        assert 0.5 <= score <= 1.0, f"Expected high compatibility score, got {score}"
        
        # Test low compatibility query
        low_compat_query = QueryAnalysis(
            complexity="complex",
            intents=["search", "web"],
            requirements={"requires_internet": True},
            confidence=0.8
        )
        
        score = self.calculator.analyze_compatibility(low_compat_query)
        assert 0.0 <= score <= 0.5, f"Expected low compatibility score, got {score}"
    
    def test_execute_with_monitoring(self):
        """Test performance monitoring during execution."""
        task = "calculate 2 + 2"
        result = self.calculator.execute_with_monitoring(task)
        
        # Check result structure
        assert "success" in result
        assert "metadata" in result
        assert "performance" in result["metadata"]
        
        # Check performance metrics
        perf = result["metadata"]["performance"]
        assert "execution_time" in perf
        assert "memory_usage_mb" in perf
        assert "api_calls_made" in perf
        assert "tool_name" in perf
        
        # Validate metric types and ranges
        assert isinstance(perf["execution_time"], (int, float))
        assert perf["execution_time"] >= 0
        assert isinstance(perf["memory_usage_mb"], (int, float))
        assert isinstance(perf["api_calls_made"], int)
        assert perf["api_calls_made"] >= 0
    
    def test_error_handling_with_monitoring(self):
        """Test error handling includes performance data."""
        result = self.calculator.execute_with_monitoring("invalid expression")
        
        # Should be an error response
        assert result["success"] is False
        assert "error" in result
        assert "metadata" in result
        assert "performance" in result["metadata"]
        
        # Performance data should still be present
        perf = result["metadata"]["performance"]
        assert "execution_time" in perf
        assert "tool_name" in perf
        # Note: Calculator handles errors gracefully, so no "failed" flag


class TestComposableTool:
    """Test suite for ComposableTool functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = CalculatorTool()
    
    def test_get_input_schema(self):
        """Test input schema generation."""
        schema = self.calculator.get_input_schema()
        
        assert "type" in schema
        assert "properties" in schema
        assert "required" in schema
        
        # Check task field is present and required
        assert "task" in schema["properties"]
        assert "task" in schema["required"]
    
    def test_get_output_schema(self):
        """Test output schema generation."""
        schema = self.calculator.get_output_schema()
        
        assert "type" in schema
        assert "properties" in schema
        assert "required" in schema
        
        # Check required output fields
        assert "success" in schema["properties"]
        assert "success" in schema["required"]
    
    def test_validate_input(self):
        """Test input validation."""
        # Valid input
        valid_input = {"task": "calculate 2 + 2"}
        assert self.calculator.validate_input(valid_input) is True
        
        # Invalid input (missing required field)
        invalid_input = {"query": "calculate 2 + 2"}
        assert self.calculator.validate_input(invalid_input) is False
        
        # Empty input
        empty_input = {}
        assert self.calculator.validate_input(empty_input) is False
    
    def test_validate_output(self):
        """Test output validation."""
        # Valid output
        valid_output = {
            "success": True,
            "data": {"result": 4},
            "metadata": {}
        }
        assert self.calculator.validate_output(valid_output) is True
        
        # Invalid output (missing required field)
        invalid_output = {
            "data": {"result": 4},
            "metadata": {}
        }
        assert self.calculator.validate_output(invalid_output) is False
    
    def test_can_chain_with(self):
        """Test tool chaining compatibility."""
        calculator1 = CalculatorTool()
        calculator2 = CalculatorTool()
        
        # Calculator output doesn't match calculator input schema
        # (output has success/data, input expects task)
        assert calculator1.can_chain_with(calculator2) is False
        
        # Test with non-composable tool
        class SimpleBaseTool(BaseTool):
            def can_handle(self, task: str) -> bool:
                return True
            def execute(self, task: str):
                return "result"
        
        simple_tool = SimpleBaseTool()
        assert calculator1.can_chain_with(simple_tool) is False
        
        # Test schema compatibility logic works
        class CompatibleTool(ComposableTool):
            def can_handle(self, task: str) -> bool:
                return True
            def execute(self, task: str):
                return {"success": True, "data": {}}
            
            def get_input_schema(self):
                # This tool accepts calculator output
                return {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "data": {"type": "object"}
                    },
                    "required": ["success"]
                }
        
        compatible_tool = CompatibleTool()
        assert calculator1.can_chain_with(compatible_tool) is True


class TestQueryAnalysis:
    """Test suite for QueryAnalysis dataclass."""
    
    def test_query_analysis_creation(self):
        """Test QueryAnalysis object creation."""
        query = QueryAnalysis(
            complexity="moderate",
            intents=["calculate", "analyze"],
            requirements={"requires_internet": False},
            confidence=0.85,
            entities=["numbers", "operations"],
            sentiment="neutral"
        )
        
        assert query.complexity == "moderate"
        assert query.intents == ["calculate", "analyze"]
        assert query.requirements == {"requires_internet": False}
        assert query.confidence == 0.85
        assert query.entities == ["numbers", "operations"]
        assert query.sentiment == "neutral"
    
    def test_query_analysis_defaults(self):
        """Test QueryAnalysis with default values."""
        query = QueryAnalysis(
            complexity="simple",
            intents=["test"],
            requirements={},
            confidence=0.9
        )
        
        assert query.entities is None
        assert query.sentiment == "neutral"


class TestPerformanceMonitoring:
    """Test suite for performance monitoring features."""
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking."""
        calculator = CalculatorTool()
        
        # Memory usage should be a non-negative number
        memory_usage = calculator._get_memory_usage()
        assert isinstance(memory_usage, (int, float))
        assert memory_usage >= 0
    
    def test_api_call_tracking(self):
        """Test API call tracking."""
        calculator = CalculatorTool()
        
        # Calculator doesn't make API calls
        api_calls = calculator._get_api_call_count()
        assert isinstance(api_calls, int)
        assert api_calls == 0
    
    def test_execution_time_measurement(self):
        """Test execution time measurement."""
        calculator = CalculatorTool()
        
        # Execute a task and check timing
        result = calculator.execute_with_monitoring("calculate 2 + 2")
        
        execution_time = result["metadata"]["performance"]["execution_time"]
        assert isinstance(execution_time, (int, float))
        assert execution_time >= 0  # Should be non-negative
        assert execution_time < 1.0  # Should be fast for simple calculation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
