"""
Graph-Enhanced Knowledge Retriever

Provides advanced search and retrieval capabilities using the knowledge graph
for contextual expansion, semantic pathfinding, and intelligent ranking.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from ..knowledge_entry import KnowledgeEntry, KnowledgeQueryResult
from .knowledge_graph import KnowledgeGraph


class GraphKnowledgeRetriever:
    """
    Graph-enhanced knowledge retrieval system
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize graph retriever
        
        Args:
            knowledge_graph: KnowledgeGraph instance
        """
        self.graph = knowledge_graph
        self.knowledge_base = knowledge_graph.knowledge_base
    
    def search_with_context(self, query: str, include_related: bool = True, 
                           max_depth: int = 2, category: Optional[str] = None,
                           tags: Optional[List[str]] = None, max_results: int = 10,
                           similarity_threshold: float = None) -> KnowledgeQueryResult:
        """
        Search with graph context expansion
        
        Args:
            query: Search query
            include_related: Whether to include related entries
            max_depth: Maximum depth for graph traversal
            category: Filter by category
            tags: Filter by tags
            max_results: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            KnowledgeQueryResult with expanded context
        """
        start_time = time.time()
        
        # First, get direct matches using traditional search (disable graph to avoid recursion)
        direct_results = self.knowledge_base.search(
            query=query,
            category=category,
            tags=tags,
            max_results=max_results,
            similarity_threshold=similarity_threshold,
            use_graph=False  # Prevent recursion
        )
        
        if not include_related or not direct_results.entries:
            # Return direct results if no expansion requested or no results found
            direct_results.execution_time = time.time() - start_time
            return direct_results
        
        # Expand results using graph context
        expanded_entries = []
        expanded_scores = []
        seen_ids = set()
        
        # Add direct results first
        for i, entry in enumerate(direct_results.entries):
            expanded_entries.append(entry)
            score = direct_results.relevance_scores[i] if i < len(direct_results.relevance_scores) else 1.0
            expanded_scores.append(score)
            seen_ids.add(entry.id)
        
        # Expand with related entries
        if include_related:
            related_entries = self._expand_with_graph_context(
                direct_results.entries, max_depth, query, seen_ids
            )
            
            for entry, score in related_entries:
                if len(expanded_entries) >= max_results:
                    break
                expanded_entries.append(entry)
                expanded_scores.append(score)
        
        # Create enhanced result
        enhanced_result = KnowledgeQueryResult(
            entries=expanded_entries,
            total_count=len(expanded_entries),
            query=query,
            filters={
                'category': category,
                'tags': tags,
                'include_related': include_related,
                'max_depth': max_depth
            },
            execution_time=time.time() - start_time,
            relevance_scores=expanded_scores
        )
        
        return enhanced_result
    
    def _expand_with_graph_context(self, seed_entries: List[KnowledgeEntry], 
                                  max_depth: int, query: str, 
                                  seen_ids: set) -> List[Tuple[KnowledgeEntry, float]]:
        """
        Expand search results using graph context
        
        Args:
            seed_entries: Initial entries to expand from
            max_depth: Maximum traversal depth
            query: Original query for relevance scoring
            seen_ids: Set of already seen entry IDs
            
        Returns:
            List of (entry, relevance_score) tuples
        """
        related_entries = []
        
        for seed_entry in seed_entries:
            # Get neighbors from graph
            neighbor_ids = self.graph.get_neighbors(
                seed_entry.id, 
                max_depth=max_depth
            )
            
            for neighbor_id in neighbor_ids:
                if neighbor_id in seen_ids:
                    continue
                
                # Get the actual entry
                neighbor_entry = self.knowledge_base.get(neighbor_id)
                if not neighbor_entry:
                    continue
                
                # Calculate relevance score for related entry
                relevance_score = self._calculate_related_relevance(
                    neighbor_entry, seed_entry, query
                )
                
                if relevance_score > 0.1:  # Minimum threshold for related entries
                    related_entries.append((neighbor_entry, relevance_score))
                    seen_ids.add(neighbor_id)
        
        # Sort by relevance score
        related_entries.sort(key=lambda x: x[1], reverse=True)
        
        return related_entries
    
    def _calculate_related_relevance(self, related_entry: KnowledgeEntry, 
                                   seed_entry: KnowledgeEntry, query: str) -> float:
        """
        Calculate relevance score for a related entry
        
        Args:
            related_entry: The related entry to score
            seed_entry: The seed entry it's related to
            query: Original search query
            
        Returns:
            Relevance score (0.0-1.0)
        """
        # Base score from direct text relevance
        base_score = self.knowledge_base._calculate_relevance(query, related_entry)
        
        # Relationship strength bonus
        relationship_bonus = 0.0
        if self.graph.graph.has_edge(seed_entry.id, related_entry.id):
            edge_data = self.graph.graph.edges[seed_entry.id, related_entry.id]
            relationship_bonus = edge_data.get('strength', 0.5) * 0.3
        elif self.graph.graph.has_edge(related_entry.id, seed_entry.id):
            edge_data = self.graph.graph.edges[related_entry.id, seed_entry.id]
            relationship_bonus = edge_data.get('strength', 0.5) * 0.3
        
        # Centrality bonus (important entries get slight boost)
        centrality_bonus = 0.0
        if related_entry.id in self.graph.graph.nodes:
            centrality = self.graph.graph.nodes[related_entry.id].get('centrality_score', 0.0)
            centrality_bonus = centrality * 0.1
        
        # Combine scores
        final_score = base_score * 0.6 + relationship_bonus + centrality_bonus
        
        return min(1.0, final_score)
    
    def semantic_walk(self, start_entry_id: str, query: str, 
                     max_steps: int = 3) -> List[KnowledgeEntry]:
        """
        Perform semantic walk through the knowledge graph
        
        Args:
            start_entry_id: Starting entry ID
            query: Query to guide the walk
            max_steps: Maximum number of steps
            
        Returns:
            List of entries found during the walk
        """
        if not self.graph.graph.has_node(start_entry_id):
            return []
        
        visited = set()
        current_entries = [start_entry_id]
        result_entries = []
        
        for step in range(max_steps):
            next_entries = []
            
            for entry_id in current_entries:
                if entry_id in visited:
                    continue
                
                visited.add(entry_id)
                
                # Get the entry
                entry = self.knowledge_base.get(entry_id)
                if entry:
                    result_entries.append(entry)
                
                # Find best neighbors based on query relevance
                neighbors = self.graph.get_neighbors(entry_id, max_depth=1)
                neighbor_scores = []
                
                for neighbor_id in neighbors:
                    if neighbor_id in visited:
                        continue
                    
                    neighbor_entry = self.knowledge_base.get(neighbor_id)
                    if neighbor_entry:
                        relevance = self.knowledge_base._calculate_relevance(query, neighbor_entry)
                        neighbor_scores.append((neighbor_id, relevance))
                
                # Sort by relevance and take top candidates
                neighbor_scores.sort(key=lambda x: x[1], reverse=True)
                next_entries.extend([nid for nid, _ in neighbor_scores[:2]])
            
            current_entries = next_entries
            if not current_entries:
                break
        
        return result_entries
    
    def find_knowledge_paths(self, source_concept: str, target_concept: str, 
                           max_paths: int = 3) -> List[List[KnowledgeEntry]]:
        """
        Find knowledge paths between two concepts
        
        Args:
            source_concept: Source concept to search for
            target_concept: Target concept to search for
            max_paths: Maximum number of paths to return
            
        Returns:
            List of paths, where each path is a list of KnowledgeEntry objects
        """
        # Find entries matching source and target concepts
        source_results = self.knowledge_base.search(source_concept, max_results=5)
        target_results = self.knowledge_base.search(target_concept, max_results=5)
        
        if not source_results.entries or not target_results.entries:
            return []
        
        paths = []
        
        # Try to find paths between each source-target pair
        for source_entry in source_results.entries[:3]:  # Limit to top 3
            for target_entry in target_results.entries[:3]:  # Limit to top 3
                if len(paths) >= max_paths:
                    break
                
                # Find shortest path in graph
                path_ids = self.graph.find_shortest_path(source_entry.id, target_entry.id)
                
                if path_ids and len(path_ids) > 1:  # Valid path found
                    # Convert IDs to entries
                    path_entries = []
                    for entry_id in path_ids:
                        entry = self.knowledge_base.get(entry_id)
                        if entry:
                            path_entries.append(entry)
                    
                    if len(path_entries) == len(path_ids):  # All entries found
                        paths.append(path_entries)
        
        return paths
    
    def get_most_connected_entries(self, limit: int = 10) -> List[Tuple[KnowledgeEntry, float]]:
        """
        Get most connected entries in the knowledge graph
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of (entry, centrality_score) tuples
        """
        central_entries = self.graph.get_most_central_entries(limit)
        result = []
        
        for entry_id, centrality_score in central_entries:
            entry = self.knowledge_base.get(entry_id)
            if entry:
                result.append((entry, centrality_score))
        
        return result
    
    def suggest_related_entries(self, entry_id: str, max_suggestions: int = 5) -> List[KnowledgeEntry]:
        """
        Suggest related entries for a given entry
        
        Args:
            entry_id: Entry ID to find suggestions for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested KnowledgeEntry objects
        """
        if not self.graph.graph.has_node(entry_id):
            return []
        
        # Get neighbors with different relationship types
        neighbors = self.graph.get_neighbors(entry_id, max_depth=2)
        
        # Score neighbors by relationship strength and centrality
        scored_neighbors = []
        
        for neighbor_id in neighbors:
            neighbor_entry = self.knowledge_base.get(neighbor_id)
            if not neighbor_entry:
                continue
            
            # Calculate suggestion score
            score = 0.0
            
            # Direct relationship bonus
            if self.graph.graph.has_edge(entry_id, neighbor_id):
                edge_data = self.graph.graph.edges[entry_id, neighbor_id]
                score += edge_data.get('strength', 0.5) * 0.7
            elif self.graph.graph.has_edge(neighbor_id, entry_id):
                edge_data = self.graph.graph.edges[neighbor_id, entry_id]
                score += edge_data.get('strength', 0.5) * 0.7
            
            # Centrality bonus
            if neighbor_id in self.graph.graph.nodes:
                centrality = self.graph.graph.nodes[neighbor_id].get('centrality_score', 0.0)
                score += centrality * 0.3
            
            scored_neighbors.append((neighbor_entry, score))
        
        # Sort by score and return top suggestions
        scored_neighbors.sort(key=lambda x: x[1], reverse=True)
        
        return [entry for entry, _ in scored_neighbors[:max_suggestions]]
