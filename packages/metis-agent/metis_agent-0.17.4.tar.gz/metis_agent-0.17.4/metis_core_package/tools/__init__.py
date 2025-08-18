"""
MCP Tools Registry

This module provides access to all available MCP tools following the new architecture.
"""

from typing import List, Type, Dict, Any, Optional
from .base import BaseTool

# Import registry functions
from .registry import (
    register_tool,
    get_tool,
    initialize_tools,
    discover_tools
)

# Core tools (Priority 1) - Essential functionality
from .core_tools.filesystem_tool import FileSystemTool
from .core_tools.google_search_tool import GoogleSearchTool
from .core_tools.calculator_tool import CalculatorTool
from .core_tools.unit_test_generator_tool import UnitTestGeneratorTool
from .core_tools.enhanced_search_tool import EnhancedSearchTool

# Utility tools (Priority 2) - Helper functionality  
from .utility_tools.validation_tool import ValidationTool
from .utility_tools.text_processing_tool import TextProcessingTool

# Advanced tools (Priority 3) - Specialized functionality
# from .advanced_tools.git_integration_tool import GitIntegrationTool
# from .advanced_tools.dependency_manager_tool import DependencyManagerTool
# from .advanced_tools.database_tool import DatabaseTool
# from .advanced_tools.api_client_tool import APIClientTool

# Export registry functions
__all__ = [
    'BaseTool',
    'register_tool',
    'get_tool',
    'initialize_tools', 
    'discover_tools',
    'get_available_tools',
    'get_tool_registry'
]


def get_available_tools() -> List[Type[BaseTool]]:
    """
    Get list of all available tool classes.
    
    Returns:
        List of tool classes that inherit from BaseTool
    """
    tools = []
    
    # Add core tools
    tools.extend([
        FileSystemTool,
        GoogleSearchTool,
        CalculatorTool,
        UnitTestGeneratorTool,
        EnhancedSearchTool
    ])
    
    # Add utility tools
    tools.extend([
        ValidationTool,
        TextProcessingTool
    ])
    
    # Add advanced tools (when implemented)
    # tools.extend([
    #     GitIntegrationTool,
    #     DependencyManagerTool,
    #     DatabaseTool,
    #     APIClientTool
    # ])
    
    return tools


def get_tool_registry() -> Dict[str, Dict[str, Any]]:
    """
    Get tool registry for MCP server.
    
    Returns:
        Dictionary mapping tool names to their metadata
    """
    registry = {}
    
    for tool_class in get_available_tools():
        tool_instance = tool_class()
        tool_name = tool_class.__name__.lower().replace('tool', '')
        
        registry[tool_name] = {
            "class": tool_class,
            "name": tool_instance.name,
            "description": tool_instance.description,
            "examples": tool_instance.get_examples()
        }
    
    return registry


# Legacy compatibility - will be removed in future versions
AVAILABLE_TOOLS = get_available_tools()
