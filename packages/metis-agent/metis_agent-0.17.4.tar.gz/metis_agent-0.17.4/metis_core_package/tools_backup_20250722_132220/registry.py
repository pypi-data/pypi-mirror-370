"""
Tool Registry for Metis Agent.

This module provides a registry for tools and functions to register and retrieve tools.
Supports enhanced MCP tool architecture with subdirectories for organization.
"""
from typing import Dict, Type, List, Any, Optional
import importlib
import inspect
import os
import sys
from .base import BaseTool, ComposableTool


# Global registry of tools
_TOOL_REGISTRY: Dict[str, Type[BaseTool]] = {}


def register_tool(name: str, tool_class: Type[BaseTool]) -> None:
    """
    Register a tool with the registry.
    
    Args:
        name: Name of the tool
        tool_class: Tool class
    """
    global _TOOL_REGISTRY
    _TOOL_REGISTRY[name] = tool_class
    print(f"Registered tool: {name}")


def get_tool(name: str) -> Optional[Type[BaseTool]]:
    """
    Get a tool from the registry.
    
    Args:
        name: Name of the tool
        
    Returns:
        Tool class or None if not found
    """
    return _TOOL_REGISTRY.get(name)


def get_available_tools() -> List[str]:
    """
    Get a list of available tools.
    
    Returns:
        List of tool names
    """
    return list(_TOOL_REGISTRY.keys())


def initialize_tools() -> Dict[str, BaseTool]:
    """
    Initialize all registered tools.
    
    Returns:
        Dictionary of tool instances
    """
    tool_instances = {}
    
    for name, tool_class in _TOOL_REGISTRY.items():
        try:
            tool_instances[name] = tool_class()
            print(f"Initialized tool: {name}")
        except Exception as e:
            print(f"Error initializing tool {name}: {e}")
            
    return tool_instances


def discover_tools(tools_dir: Optional[str] = None) -> None:
    """
    Discover and register tools from the tools directory and subdirectories.
    
    Supports enhanced MCP architecture with tool categories in subdirectories:
    - core_tools: Basic utility tools
    - utility_tools: General purpose tools
    - advanced_tools: Complex and specialized tools
    
    Args:
        tools_dir: Directory to search for tools (default: current module directory)
    """
    if tools_dir is None:
        # Use the directory of this file
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        
    # Get all Python files in the tools directory and subdirectories
    if not os.path.exists(tools_dir):
        print(f"Tools directory not found: {tools_dir}")
        return
    
    # First discover root directory tools
    _discover_tools_in_directory(tools_dir)
    
    # Then discover tools in subdirectories
    subdirectories = [
        'core_tools', 
        'utility_tools', 
        'advanced_tools'
    ]
    
    for subdir in subdirectories:
        subdir_path = os.path.join(tools_dir, subdir)
        if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
            _discover_tools_in_directory(subdir_path)
            
    print(f"Discovered {len(_TOOL_REGISTRY)} total tools")


def _discover_tools_in_directory(directory: str) -> None:
    """
    Discover and register tools from the specified directory.
    
    Args:
        directory: Directory to search for tools
    """
    if not os.path.exists(directory):
        return
        
    files = [f[:-3] for f in os.listdir(directory) 
            if f.endswith('.py') and not f.startswith('__') and f != 'registry.py' and f != 'base.py']
    
    # Import each tool module
    for module_name in files:
        try:
            # Get relative path from tools directory to module
            tools_dir = os.path.dirname(os.path.abspath(__file__))
            rel_path = os.path.relpath(directory, tools_dir)
            
            # Construct the full module name
            if directory == tools_dir:
                # If directory is the root tools directory, use simple relative import
                full_module_name = f".{module_name}"
            else:
                # If in subdirectory, include subdirectory in import
                subdir_name = os.path.basename(directory)
                full_module_name = f".{subdir_name}.{module_name}"
            
            module = importlib.import_module(full_module_name, package=__package__)
            
            # Find tool classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj != BaseTool and obj != ComposableTool:
                    register_tool(name, obj)
                    
        except Exception as e:
            print(f"Error loading tool module {module_name} from {directory}: {e}")


# Auto-discover tools when the module is imported
discover_tools()