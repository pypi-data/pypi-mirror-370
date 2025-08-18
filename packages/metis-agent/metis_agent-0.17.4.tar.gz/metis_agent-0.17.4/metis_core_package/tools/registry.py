"""
Tool Registry for Metis Agent.

This module provides a registry for tools and functions to register and retrieve tools.
"""
from typing import Dict, Type, List, Any, Optional
import importlib
import inspect
import os
import sys
from .base import BaseTool


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
    # print(f"Registered tool: {name}")  # Disabled to reduce CLI noise


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


def clear_registry() -> None:
    """Clear all registered tools."""
    global _TOOL_REGISTRY
    _TOOL_REGISTRY.clear()


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
    
    Args:
        tools_dir: Directory to search for tools (default: current module directory)
    """
    if tools_dir is None:
        # Use the directory of this file
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        
    if not os.path.exists(tools_dir):
        print(f"Tools directory not found: {tools_dir}")
        return
    
    def _discover_in_directory(directory: str, package_prefix: str = ""):
        """Recursively discover tools in a directory."""
        # Get all Python files in the current directory
        files = [f[:-3] for f in os.listdir(directory) 
                if f.endswith('.py') and not f.startswith('__') and f != 'registry.py' and f != 'base.py']
        
        # Import each tool module
        for module_name in files:
            try:
                # Construct the full module name with package prefix
                full_module_name = f"{package_prefix}.{module_name}" if package_prefix else module_name
                
                # Import the module
                if directory == tools_dir:
                    # Main tools directory - use relative import
                    module = importlib.import_module(f".{full_module_name}", package=__package__)
                else:
                    # Subdirectory - use relative import with subdirectory
                    rel_path = os.path.relpath(directory, tools_dir).replace(os.sep, '.')
                    module = importlib.import_module(f".{rel_path}.{module_name}", package=__package__)
                
                # Find tool classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseTool) and obj != BaseTool:
                        register_tool(name, obj)
                        
            except Exception as e:
                print(f"Error loading tool module {full_module_name}: {e}")
        
        # Recursively search subdirectories
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and not item.startswith('__') and item != 'tests':
                # Skip common non-tool directories
                if item in ['__pycache__', '.git', '.pytest_cache', 'tests']:
                    continue
                    
                # Recursively discover in subdirectory
                sub_package_prefix = f"{package_prefix}.{item}" if package_prefix else item
                _discover_in_directory(item_path, sub_package_prefix)
    
    # Start discovery from the main tools directory
    _discover_in_directory(tools_dir)
    
    print(f"Discovered {len(_TOOL_REGISTRY)} tools")


# Auto-discover tools when the module is imported
discover_tools()