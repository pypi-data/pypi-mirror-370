"""
Memory package for Metis Agent.

This package provides memory implementations for the agent, including
isolated memory management for multi-agent systems.
"""
from .memory_interface import MemoryInterface
from .sqlite_store import SQLiteMemory
from .isolated_memory import (
    AgentMemoryManager,
    IsolatedMemoryStore,
    SQLiteIsolatedMemory,
    MemoryBoundary,
    MemoryStats,
    get_memory_manager,
    configure_memory_manager
)

__all__ = [
    'MemoryInterface',
    'SQLiteMemory',
    'AgentMemoryManager',
    'IsolatedMemoryStore',
    'SQLiteIsolatedMemory',
    'MemoryBoundary',
    'MemoryStats',
    'get_memory_manager',
    'configure_memory_manager'
]