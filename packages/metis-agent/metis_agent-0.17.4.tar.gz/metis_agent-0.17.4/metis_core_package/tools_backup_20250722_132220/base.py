"""
Enhanced Base Tool interface for Metis Agent.

This module defines the enhanced base class with capabilities metadata,
performance monitoring, and composition support.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import time
import os
import json
from dataclasses import dataclass

# Optional dependency - graceful fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class QueryAnalysis:
    """
    Data class for query analysis results.
    """
    complexity: str  # simple, moderate, complex
    intents: List[str]  # List of detected intents
    requirements: Dict[str, Any]  # Resource requirements
    confidence: float  # Confidence in analysis (0-1)
    entities: List[str] = None  # Extracted entities
    sentiment: str = "neutral"  # positive, negative, neutral


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    All tools must implement the can_handle and execute methods.
    """
    
    @abstractmethod
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if the tool can handle the task, False otherwise
        """
        pass
        
    @abstractmethod
    def execute(self, task: str) -> Any:
        """
        Execute the task using this tool.
        
        Args:
            task: The task to execute
            
        Returns:
            The result of executing the task
        """
        pass
        
    def get_description(self) -> str:
        """
        Get a description of this tool.
        
        Returns:
            Tool description
        """
        # Default to using the class docstring
        return self.__doc__ or f"{self.__class__.__name__} Tool"
        
    def get_examples(self) -> list:
        """
        Get example tasks that this tool can handle.
        
        Returns:
            List of example tasks
        """
        # Default to empty list, should be overridden by subclasses
        return []
        
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.__class__.__name__}"
        
    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return f"{self.__class__.__name__}()"
    
    # Enhanced functionality methods
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return detailed capability metadata for analysis engine.
        
        Returns:
            Dictionary containing tool capabilities and requirements
        """
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text"],
            "output_types": ["structured_data"],
            "estimated_execution_time": "1-5s",
            "requires_internet": False,
            "requires_filesystem": False,
            "concurrent_safe": True,
            "resource_intensive": False,
            "supported_intents": [],
            "api_dependencies": [],
            "memory_usage": "low"
        }
    
    def analyze_compatibility(self, query_analysis: 'QueryAnalysis') -> float:
        """
        Return compatibility score (0-1) for this query analysis.
        
        Args:
            query_analysis: Analysis of the user query
            
        Returns:
            Compatibility score between 0 and 1
        """
        capabilities = self.get_capabilities()
        score = 0.0
        
        # Check complexity compatibility
        if hasattr(query_analysis, 'complexity') and query_analysis.complexity in capabilities.get("complexity_levels", []):
            score += 0.4
        
        # Check intent alignment
        if hasattr(query_analysis, 'intents'):
            supported_intents = capabilities.get("supported_intents", [])
            if any(intent in supported_intents for intent in query_analysis.intents):
                score += 0.4
        
        # Check resource requirements
        if hasattr(query_analysis, 'requirements'):
            if self._can_meet_resource_requirements(query_analysis.requirements):
                score += 0.2
        else:
            score += 0.2  # Default if no specific requirements
        
        return min(score, 1.0)
    
    def _can_meet_resource_requirements(self, requirements: Dict[str, Any]) -> bool:
        """
        Check if tool can meet specified resource requirements.
        
        Args:
            requirements: Dictionary of resource requirements
            
        Returns:
            True if requirements can be met
        """
        capabilities = self.get_capabilities()
        
        # Check internet requirement
        if requirements.get("requires_internet", False) and not capabilities.get("requires_internet", False):
            return False
        
        # Check filesystem requirement
        if requirements.get("requires_filesystem", False) and not capabilities.get("requires_filesystem", False):
            return False
        
        # Check if tool is resource intensive when low resource usage is required
        if requirements.get("low_resource", False) and capabilities.get("resource_intensive", False):
            return False
        
        return True
    
    def execute_with_monitoring(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute task with performance monitoring.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            Result with performance metadata
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        api_calls_before = self._get_api_call_count()
        
        try:
            result = self.execute(task, **kwargs)
            execution_time = time.time() - start_time
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                result = {"data": result, "success": True}
            
            # Add performance metadata
            if "metadata" not in result:
                result["metadata"] = {}
            
            result["metadata"]["performance"] = {
                "execution_time": round(execution_time, 4),
                "memory_usage_mb": self._get_memory_usage() - start_memory,
                "api_calls_made": self._get_api_call_count() - api_calls_before,
                "tool_name": self.__class__.__name__
            }
            
            return result
            
        except Exception as e:
            return self._handle_execution_error(e, time.time() - start_time)
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
        """
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def _get_api_call_count(self) -> int:
        """
        Get number of API calls made (to be overridden by tools that make API calls).
        
        Returns:
            Number of API calls made
        """
        return 0
    
    def _handle_execution_error(self, error: Exception, execution_time: float) -> Dict[str, Any]:
        """
        Handle execution errors with performance data.
        
        Args:
            error: The exception that occurred
            execution_time: Time taken before error
            
        Returns:
            Error response with metadata
        """
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "metadata": {
                "tool_name": self.__class__.__name__,
                "performance": {
                    "execution_time": round(execution_time, 4),
                    "failed": True
                }
            }
        }


class ComposableTool(BaseTool):
    """
    Base class for tools that can be composed in pipelines.
    
    Provides schema validation and tool chaining capabilities.
    """
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for input validation.
        
        Returns:
            JSON schema dictionary for input validation
        """
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task to execute"
                }
            },
            "required": ["task"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for output validation.
        
        Returns:
            JSON schema dictionary for output validation
        """
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the operation was successful"
                },
                "data": {
                    "type": "object",
                    "description": "The result data"
                },
                "metadata": {
                    "type": "object",
                    "description": "Operation metadata"
                }
            },
            "required": ["success"]
        }
    
    def can_chain_with(self, other_tool: 'BaseTool') -> bool:
        """
        Check if this tool's output is compatible with another tool's input.
        
        Args:
            other_tool: The tool to check compatibility with
            
        Returns:
            True if tools can be chained
        """
        if not isinstance(other_tool, ComposableTool):
            return False
        
        return self._schemas_compatible(
            self.get_output_schema(),
            other_tool.get_input_schema()
        )
    
    def _schemas_compatible(self, output_schema: Dict[str, Any], input_schema: Dict[str, Any]) -> bool:
        """
        Check if output schema is compatible with input schema.
        
        Args:
            output_schema: Schema of output data
            input_schema: Schema of required input data
            
        Returns:
            True if schemas are compatible
        """
        # Basic compatibility check
        # In a full implementation, this would do deep schema validation
        
        output_props = output_schema.get("properties", {})
        input_props = input_schema.get("properties", {})
        input_required = input_schema.get("required", [])
        
        # Check if all required input properties are available in output
        for required_prop in input_required:
            if required_prop not in output_props:
                return False
        
        return True
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid
        """
        schema = self.get_input_schema()
        required_fields = schema.get("required", [])
        
        # Basic validation - check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    def validate_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate output data against output schema.
        
        Args:
            data: Output data to validate
            
        Returns:
            True if data is valid
        """
        schema = self.get_output_schema()
        required_fields = schema.get("required", [])
        
        # Basic validation - check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        return True