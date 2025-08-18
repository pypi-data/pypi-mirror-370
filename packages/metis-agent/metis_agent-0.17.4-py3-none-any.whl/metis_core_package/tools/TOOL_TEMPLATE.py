"""
Template for creating new MCP tools.

Copy this file and rename it to your tool name (e.g., web_search_tool.py).
Follow the MCP Tool Development Guide for best practices.
"""

from typing import Any, Dict, List, Optional
import os
import datetime
from .base import BaseTool


class TemplateTool(BaseTool):
    """
    Template tool for MCP server.
    
    Replace this docstring with a clear description of what your tool does.
    
    This tool should NOT:
    - Initialize LLM instances
    - Store state between calls
    - Perform operations outside its scope
    
    This tool SHOULD:
    - Be stateless and deterministic
    - Validate inputs thoroughly
    - Return structured, consistent outputs
    """
    
    def __init__(self):
        """Initialize tool with configuration only."""
        self.name = "Template Tool"  # Replace with your tool name
        self.description = "Template tool for creating new MCP tools"  # Replace with your description
        
        # Add any configuration here (but NO LLM initialization!)
        self.supported_formats = ["json", "text", "xml"]  # Example configuration
        self.max_input_length = 10000  # Example limit
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this tool can handle the given task.
        
        Args:
            task: The task description
            
        Returns:
            True if tool can handle the task, False otherwise
        """
        if not task or not task.strip():
            return False
        
        task_lower = task.lower().strip()
        
        # Define keywords that indicate this tool should handle the task
        keywords = [
            "template",
            "example",
            "test"
        ]
        
        # Check for explicit keywords
        if any(keyword in task_lower for keyword in keywords):
            return True
        
        # Add more sophisticated logic here
        # For example, check for specific patterns or phrases
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool's functionality.
        
        Args:
            task: The primary task description
            **kwargs: Additional parameters (API keys, options, etc.)
            
        Returns:
            Structured dictionary with results
        """
        # Input validation
        if not task or not task.strip():
            return self._format_error_response(
                "Task cannot be empty",
                "INVALID_INPUT",
                ["Provide a non-empty task description"]
            )
        
        if len(task) > self.max_input_length:
            return self._format_error_response(
                f"Task too long (max {self.max_input_length} characters)",
                "INPUT_TOO_LONG",
                [f"Reduce task length to under {self.max_input_length} characters"]
            )
        
        try:
            # Extract parameters from kwargs
            output_format = kwargs.get('format', 'json')
            api_key = kwargs.get('api_key')  # If your tool needs API keys
            
            # Validate format
            if output_format not in self.supported_formats:
                return self._format_error_response(
                    f"Unsupported format: {output_format}",
                    "INVALID_FORMAT",
                    [f"Supported formats: {', '.join(self.supported_formats)}"]
                )
            
            # Main tool logic goes here
            result_data = self._process_task(task, **kwargs)
            
            # Format and return success response
            return self._format_success_response(
                result_data,
                {"format": output_format, "task_length": len(task)}
            )
            
        except Exception as e:
            return self._format_error_response(
                f"Error processing task: {str(e)}",
                "PROCESSING_ERROR",
                ["Check task format and try again", "Verify all required parameters are provided"]
            )
    
    def _process_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Process the main task logic.
        
        Args:
            task: The task to process
            **kwargs: Additional parameters
            
        Returns:
            Processed data
        """
        # Replace this with your actual tool logic
        return {
            "processed_task": task,
            "task_length": len(task),
            "word_count": len(task.split()),
            "uppercase": task.upper(),
            "lowercase": task.lower(),
            "parameters": kwargs
        }
    
    def get_examples(self) -> List[str]:
        """Return example tasks this tool can handle."""
        return [
            "template example task",
            "test the template functionality",
            "example of template usage"
        ]
    
    def _format_success_response(self, data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a successful response."""
        return {
            "success": True,
            "type": f"{self.__class__.__name__.lower()}_response",
            "data": data,
            "metadata": {
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.datetime.now().isoformat(),
                **(metadata or {})
            }
        }
    
    def _format_error_response(self, error: str, error_code: str, suggestions: List[str] = None) -> Dict[str, Any]:
        """Format an error response."""
        return {
            "success": False,
            "error": error,
            "error_code": error_code,
            "suggestions": suggestions or [],
            "metadata": {
                "tool_name": self.__class__.__name__,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    
    def _get_api_key(self, kwargs: Dict[str, Any], key_names: List[str] = None) -> Optional[str]:
        """
        Extract API key from kwargs with fallback to environment.
        
        Args:
            kwargs: Keyword arguments
            key_names: List of possible key names to check
            
        Returns:
            API key if found, None otherwise
        """
        if key_names is None:
            key_names = ['api_key']
        
        # Check kwargs first
        for key_name in key_names:
            if key_name in kwargs and kwargs[key_name]:
                return kwargs[key_name]
        
        # Check environment variables
        env_names = [name.upper() for name in key_names]
        for env_name in env_names:
            env_value = os.getenv(env_name)
            if env_value:
                return env_value
        
        return None
