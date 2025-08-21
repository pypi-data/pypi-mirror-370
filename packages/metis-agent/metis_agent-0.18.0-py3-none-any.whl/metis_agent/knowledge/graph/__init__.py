"""
Graph Knowledge Base Module

Provides graph-enhanced knowledge base functionality including:
- In-memory graph representation using NetworkX
- Contextual search and retrieval
- Relationship detection and analysis
- Knowledge gap identification
"""

from .knowledge_graph import KnowledgeGraph
from .graph_retriever import GraphKnowledgeRetriever
from .relationship_analyzer import RelationshipAnalyzer

__all__ = [
    'KnowledgeGraph',
    'GraphKnowledgeRetriever', 
    'RelationshipAnalyzer'
]
