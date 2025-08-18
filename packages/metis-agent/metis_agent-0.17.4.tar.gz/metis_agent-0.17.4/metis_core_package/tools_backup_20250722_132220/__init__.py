"""
Tools package for Metis Agent.

This package provides various tools for the agent to use.
"""
from .base import BaseTool
from .registry import register_tool, get_tool, get_available_tools, initialize_tools, discover_tools
from .code_generation import CodeGenerationTool
from .content_generation import ContentGenerationTool
from .google_search import GoogleSearchTool
from .firecrawl import FirecrawlTool
from .filesystem import FileSystemTool
from .project_context import ProjectContextTool
from .code_analysis import CodeAnalysisTool
from .context_aware_generator import ContextAwareCodeGenerator
from .enhanced_project_generator import EnhancedProjectGeneratorTool

# Register built-in tools
register_tool("CodeGenerationTool", CodeGenerationTool)
register_tool("ContentGenerationTool", ContentGenerationTool)
register_tool("GoogleSearchTool", GoogleSearchTool)
register_tool("FirecrawlTool", FirecrawlTool)
register_tool("FileSystemTool", FileSystemTool)
register_tool("ProjectContextTool", ProjectContextTool)
register_tool("CodeAnalysisTool", CodeAnalysisTool)
register_tool("ContextAwareCodeGenerator", ContextAwareCodeGenerator)
register_tool("EnhancedProjectGeneratorTool", EnhancedProjectGeneratorTool)

__all__ = [
    'BaseTool',
    'register_tool',
    'get_tool',
    'get_available_tools',
    'initialize_tools',
    'discover_tools',
    'CodeGenerationTool',
    'ContentGenerationTool',
    'GoogleSearchTool',
    'FirecrawlTool',
    'FileSystemTool',
    'ProjectContextTool'
]