"""
Metis Agent Knowledge Base System

This module provides a comprehensive knowledge base system that extends beyond
conversational memory to include domain-specific knowledge, user-configurable
categories, and modular architecture for different knowledge types.

Knowledge Base Package

Provides modular, configurable knowledge base functionality for the Metis Agent,
including shared knowledge base for multi-agent collaboration.
"""

from .knowledge_entry import KnowledgeEntry, KnowledgeQueryResult
from .knowledge_config import KnowledgeConfig
from .knowledge_base import KnowledgeBase
from .knowledge_adapter import KnowledgeAdapter
from .shared_knowledge import (
    SharedKnowledgeBase,
    KnowledgeEntry as SharedKnowledgeEntry,
    KnowledgeACL,
    KnowledgeVersion,
    KnowledgeStats,
    get_shared_knowledge,
    configure_shared_knowledge
)

__all__ = [
    "KnowledgeEntry",
    "KnowledgeQueryResult", 
    "KnowledgeConfig",
    "KnowledgeBase",
    "KnowledgeAdapter",
    "SharedKnowledgeBase",
    "SharedKnowledgeEntry",
    "KnowledgeACL",
    "KnowledgeVersion",
    "KnowledgeStats",
    "get_shared_knowledge",
    "configure_shared_knowledge"
]

__version__ = "1.0.0"
