"""
Knowledge Graph Implementation

Provides in-memory graph representation of knowledge base entries and their
relationships using NetworkX for efficient graph operations and analysis.
"""

import networkx as nx
import sqlite3
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict

from ..knowledge_entry import KnowledgeEntry


class KnowledgeGraph:
    """
    In-memory graph representation of knowledge base using NetworkX
    """
    
    def __init__(self, knowledge_base):
        """
        Initialize knowledge graph
        
        Args:
            knowledge_base: Reference to the KnowledgeBase instance
        """
        self.knowledge_base = knowledge_base
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.entry_cache = {}  # Cache for quick entry lookup
        self.last_rebuild = None
        self.relationship_types = {
            'related_to': 1.0,
            'depends_on': 0.9,
            'extends': 0.8,
            'implements': 0.8,
            'example_of': 0.7,
            'part_of': 0.9,
            'similar_to': 0.8,
            'references': 0.6,
            'contradicts': 0.5
        }
        
        # Build initial graph
        self.build_graph_from_db()
    
    def build_graph_from_db(self) -> None:
        """
        Build the in-memory graph from database entries and relationships
        """
        print("Building knowledge graph from database...")
        start_time = time.time()
        
        try:
            # Clear existing graph
            self.graph.clear()
            self.entry_cache.clear()
            
            # Add all entries as nodes
            self._add_entries_to_graph()
            
            # Add explicit relationships from database
            self._add_relationships_to_graph()
            
            # Calculate and cache centrality scores
            self._calculate_centrality_scores()
            
            self.last_rebuild = datetime.now()
            build_time = time.time() - start_time
            
            print(f"Graph built successfully:")
            print(f"  - Nodes: {self.graph.number_of_nodes()}")
            print(f"  - Edges: {self.graph.number_of_edges()}")
            print(f"  - Build time: {build_time:.2f}s")
            
        except Exception as e:
            print(f"Error building graph: {e}")
            # Initialize empty graph as fallback
            self.graph = nx.DiGraph()
            self.entry_cache = {}
    
    def _add_entries_to_graph(self) -> None:
        """Add all knowledge entries as nodes to the graph"""
        with sqlite3.connect(self.knowledge_base.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, content, category, tags, created_at, updated_at
                FROM knowledge_entries
            ''')
            
            for row in cursor.fetchall():
                entry_id, title, content, category, tags_json, created_at, updated_at = row
                
                # Parse tags
                tags = json.loads(tags_json) if tags_json else []
                
                # Add node with attributes
                self.graph.add_node(entry_id, 
                    title=title,
                    category=category,
                    tags=tags,
                    content_length=len(content),
                    created_at=created_at,
                    updated_at=updated_at,
                    centrality_score=0.0
                )
                
                # Cache entry metadata for quick access
                self.entry_cache[entry_id] = {
                    'title': title,
                    'category': category,
                    'tags': tags,
                    'content_length': len(content)
                }
    
    def _add_relationships_to_graph(self) -> None:
        """Add explicit relationships from database as edges"""
        with sqlite3.connect(self.knowledge_base.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT source_id, target_id, relationship_type, strength, usage_count
                FROM knowledge_relationships
                WHERE source_id IN (SELECT id FROM knowledge_entries)
                AND target_id IN (SELECT id FROM knowledge_entries)
            ''')
            
            for row in cursor.fetchall():
                source_id, target_id, rel_type, strength, usage_count = row
                
                # Skip if nodes don't exist
                if not (self.graph.has_node(source_id) and self.graph.has_node(target_id)):
                    continue
                
                # Calculate edge weight based on relationship type and usage
                base_weight = self.relationship_types.get(rel_type, 0.5)
                usage_boost = min(0.3, (usage_count or 0) * 0.05)  # Max 0.3 boost
                edge_weight = min(1.0, base_weight + usage_boost)
                
                # Add edge
                self.graph.add_edge(source_id, target_id,
                    relationship_type=rel_type,
                    strength=strength or base_weight,
                    weight=edge_weight,
                    usage_count=usage_count or 0
                )
    
    def _calculate_centrality_scores(self) -> None:
        """Calculate and store centrality scores for all nodes"""
        if self.graph.number_of_nodes() == 0:
            return
        
        try:
            # Calculate different centrality measures
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness_centrality = nx.betweenness_centrality(self.graph)
            
            # For very large graphs, use approximation
            if self.graph.number_of_nodes() > 1000:
                closeness_centrality = nx.closeness_centrality(self.graph, distance='weight')
            else:
                closeness_centrality = nx.closeness_centrality(self.graph, distance='weight')
            
            # Combine centrality measures
            for node_id in self.graph.nodes():
                combined_centrality = (
                    degree_centrality.get(node_id, 0) * 0.4 +
                    betweenness_centrality.get(node_id, 0) * 0.4 +
                    closeness_centrality.get(node_id, 0) * 0.2
                )
                
                # Update node attribute
                self.graph.nodes[node_id]['centrality_score'] = combined_centrality
                
                # Update database
                self._update_centrality_in_db(node_id, combined_centrality)
                
        except Exception as e:
            print(f"Warning: Error calculating centrality scores: {e}")
    
    def _update_centrality_in_db(self, entry_id: str, centrality_score: float) -> None:
        """Update centrality score in database"""
        try:
            with sqlite3.connect(self.knowledge_base.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE knowledge_entries 
                    SET centrality_score = ?, connection_count = ?
                    WHERE id = ?
                ''', (centrality_score, self.graph.degree(entry_id), entry_id))
        except Exception as e:
            print(f"Warning: Error updating centrality in database: {e}")
    
    def add_entry_to_graph(self, entry: KnowledgeEntry) -> None:
        """
        Add a new entry to the graph
        
        Args:
            entry: KnowledgeEntry to add
        """
        # Add node
        self.graph.add_node(entry.id,
            title=entry.title,
            category=entry.category,
            tags=entry.tags,
            content_length=len(entry.content),
            created_at=entry.created_at.isoformat(),
            updated_at=entry.updated_at.isoformat(),
            centrality_score=0.0
        )
        
        # Update cache
        self.entry_cache[entry.id] = {
            'title': entry.title,
            'category': entry.category,
            'tags': entry.tags,
            'content_length': len(entry.content)
        }
        
        # Auto-detect relationships with existing entries
        self._auto_detect_relationships(entry)
    
    def _auto_detect_relationships(self, entry: KnowledgeEntry) -> None:
        """
        Automatically detect relationships for a new entry
        
        Args:
            entry: KnowledgeEntry to analyze for relationships
        """
        # Simple relationship detection based on tags and categories
        for node_id in self.graph.nodes():
            if node_id == entry.id:
                continue
            
            node_data = self.graph.nodes[node_id]
            relationship_strength = 0.0
            relationship_type = 'related_to'
            
            # Category similarity
            if node_data['category'] == entry.category:
                relationship_strength += 0.3
            
            # Tag overlap
            common_tags = set(entry.tags) & set(node_data['tags'])
            if common_tags:
                relationship_strength += len(common_tags) * 0.2
            
            # Title similarity (basic)
            if any(word.lower() in node_data['title'].lower() 
                   for word in entry.title.lower().split() if len(word) > 3):
                relationship_strength += 0.2
            
            # Add relationship if strength is significant
            if relationship_strength >= 0.4:
                self.add_relationship(entry.id, node_id, relationship_type, relationship_strength)
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relationship_type: str, strength: float = None) -> bool:
        """
        Add a relationship between two entries
        
        Args:
            source_id: Source entry ID
            target_id: Target entry ID
            relationship_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
            
        Returns:
            bool: True if relationship was added successfully
        """
        # Validate nodes exist
        if not (self.graph.has_node(source_id) and self.graph.has_node(target_id)):
            return False
        
        # Calculate strength if not provided
        if strength is None:
            strength = self.relationship_types.get(relationship_type, 0.5)
        
        # Add edge
        self.graph.add_edge(source_id, target_id,
            relationship_type=relationship_type,
            strength=strength,
            weight=strength,
            usage_count=0,
            created_at=datetime.now().isoformat()
        )
        
        # Store in database
        self._store_relationship_in_db(source_id, target_id, relationship_type, strength)
        
        return True
    
    def _store_relationship_in_db(self, source_id: str, target_id: str, 
                                 relationship_type: str, strength: float) -> None:
        """Store relationship in database"""
        try:
            with sqlite3.connect(self.knowledge_base.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_relationships
                    (source_id, target_id, relationship_type, strength, usage_count, created_at)
                    VALUES (?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                ''', (source_id, target_id, relationship_type, strength))
        except Exception as e:
            print(f"Warning: Error storing relationship in database: {e}")
    
    def get_neighbors(self, entry_id: str, max_depth: int = 1, 
                     relationship_types: Optional[List[str]] = None) -> List[str]:
        """
        Get neighboring entries up to specified depth
        
        Args:
            entry_id: Entry ID to find neighbors for
            max_depth: Maximum depth to traverse
            relationship_types: Filter by relationship types
            
        Returns:
            List of neighboring entry IDs
        """
        if not self.graph.has_node(entry_id):
            return []
        
        neighbors = set()
        current_level = {entry_id}
        
        for depth in range(max_depth):
            next_level = set()
            
            for node in current_level:
                # Get outgoing neighbors
                for neighbor in self.graph.successors(node):
                    edge_data = self.graph.edges[node, neighbor]
                    
                    # Filter by relationship type if specified
                    if relationship_types and edge_data.get('relationship_type') not in relationship_types:
                        continue
                    
                    if neighbor not in neighbors and neighbor != entry_id:
                        neighbors.add(neighbor)
                        next_level.add(neighbor)
                
                # Get incoming neighbors
                for neighbor in self.graph.predecessors(node):
                    edge_data = self.graph.edges[neighbor, node]
                    
                    # Filter by relationship type if specified
                    if relationship_types and edge_data.get('relationship_type') not in relationship_types:
                        continue
                    
                    if neighbor not in neighbors and neighbor != entry_id:
                        neighbors.add(neighbor)
                        next_level.add(neighbor)
            
            current_level = next_level
            if not current_level:
                break
        
        return list(neighbors)
    
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two entries
        
        Args:
            source_id: Source entry ID
            target_id: Target entry ID
            
        Returns:
            List of entry IDs forming the shortest path, or None if no path exists
        """
        if not (self.graph.has_node(source_id) and self.graph.has_node(target_id)):
            return None
        
        try:
            # Use weight as distance (lower weight = closer relationship)
            path = nx.shortest_path(self.graph, source_id, target_id, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_most_central_entries(self, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get entries with highest centrality scores
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of (entry_id, centrality_score) tuples
        """
        centrality_scores = []
        
        for node_id in self.graph.nodes():
            centrality = self.graph.nodes[node_id].get('centrality_score', 0.0)
            centrality_scores.append((node_id, centrality))
        
        # Sort by centrality score (descending)
        centrality_scores.sort(key=lambda x: x[1], reverse=True)
        
        return centrality_scores[:limit]
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics
        
        Returns:
            Dictionary containing graph statistics
        """
        stats = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph),
            'last_rebuild': self.last_rebuild.isoformat() if self.last_rebuild else None
        }
        
        # Add component information
        if stats['nodes'] > 0:
            components = list(nx.weakly_connected_components(self.graph))
            stats['components'] = len(components)
            stats['largest_component_size'] = len(max(components, key=len)) if components else 0
        
        # Add relationship type distribution
        relationship_counts = defaultdict(int)
        for _, _, edge_data in self.graph.edges(data=True):
            rel_type = edge_data.get('relationship_type', 'unknown')
            relationship_counts[rel_type] += 1
        
        stats['relationship_types'] = dict(relationship_counts)
        
        return stats
    
    def rebuild_if_needed(self, force: bool = False) -> bool:
        """
        Rebuild graph if needed based on database changes
        
        Args:
            force: Force rebuild regardless of last rebuild time
            
        Returns:
            bool: True if graph was rebuilt
        """
        if force or self._needs_rebuild():
            self.build_graph_from_db()
            return True
        return False
    
    def _needs_rebuild(self) -> bool:
        """Check if graph needs rebuilding based on database changes"""
        if not self.last_rebuild:
            return True
        
        # Check if there are newer entries or relationships
        try:
            with sqlite3.connect(self.knowledge_base.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for newer entries
                cursor.execute('''
                    SELECT COUNT(*) FROM knowledge_entries 
                    WHERE updated_at > ?
                ''', (self.last_rebuild.isoformat(),))
                
                if cursor.fetchone()[0] > 0:
                    return True
                
                # Check for newer relationships
                cursor.execute('''
                    SELECT COUNT(*) FROM knowledge_relationships 
                    WHERE created_at > ?
                ''', (self.last_rebuild.isoformat(),))
                
                if cursor.fetchone()[0] > 0:
                    return True
                
        except Exception as e:
            print(f"Warning: Error checking rebuild status: {e}")
            return True
        
        return False
