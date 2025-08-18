"""
Metis Agent - A framework for building powerful AI agents.

This package provides a modular architecture for building agents that can understand
user queries, plan tasks, select appropriate tools, and execute actions.
"""
from .core import SingleAgent, get_llm, configure_llm
from .tools import BaseTool, register_tool, get_tool, get_available_tools, initialize_tools
from .memory import MemoryInterface, SQLiteMemory
from .memory.titans import TitansInspiredMemory, TitansMemoryAdapter, TitansAnalytics, MemoryMonitor
from .auth import APIKeyManager, CredentialsManager, SecureStorage
from .web import format_response_for_frontend, extract_code_blocks, extract_tasks

__version__ = "0.4.1"

__all__ = [
    'SingleAgent',  # Now uses enhanced architecture by default
    'get_llm',
    'configure_llm',
    'BaseTool',
    'register_tool',
    'get_tool',
    'get_available_tools',
    'initialize_tools',
    'MemoryInterface',
    'SQLiteMemory',
    'TitansInspiredMemory',
    'TitansMemoryAdapter',
    'TitansAnalytics',
    'MemoryMonitor',
    'APIKeyManager',
    'CredentialsManager',
    'SecureStorage',
    'format_response_for_frontend',
    'extract_code_blocks',
    'extract_tasks',
    '__version__'
]