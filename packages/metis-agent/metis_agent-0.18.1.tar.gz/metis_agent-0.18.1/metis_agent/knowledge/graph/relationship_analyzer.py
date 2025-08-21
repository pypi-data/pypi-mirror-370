"""
Relationship Analyzer

Provides automatic relationship detection and analysis for knowledge entries
using various techniques including text similarity, semantic analysis, and LLM-powered detection.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from difflib import SequenceMatcher

from ..knowledge_entry import KnowledgeEntry


class RelationshipAnalyzer:
    """
    Analyzes and detects relationships between knowledge entries
    """
    
    def __init__(self, knowledge_base):
        """
        Initialize relationship analyzer
        
        Args:
            knowledge_base: Reference to KnowledgeBase instance
        """
        self.knowledge_base = knowledge_base
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
        
        # Keywords that indicate specific relationship types
        self.relationship_keywords = {
            'depends_on': ['requires', 'needs', 'depends on', 'prerequisite', 'based on'],
            'extends': ['extends', 'builds on', 'expands', 'enhances', 'improves'],
            'implements': ['implements', 'realizes', 'executes', 'applies', 'uses'],
            'example_of': ['example', 'instance', 'case study', 'demonstration', 'sample'],
            'part_of': ['part of', 'component', 'element', 'section', 'module'],
            'contradicts': ['contradicts', 'conflicts', 'opposes', 'disagrees', 'disputes'],
            'references': ['see also', 'refer to', 'mentioned in', 'cited by', 'links to']
        }
    
    def detect_content_relationships(self, entry: KnowledgeEntry) -> List[Tuple[str, str, float]]:
        """
        Detect relationships based on content analysis
        
        Args:
            entry: KnowledgeEntry to analyze
            
        Returns:
            List of (target_entry_id, relationship_type, strength) tuples
        """
        relationships = []
        
        # Get all other entries for comparison
        all_entries = self.knowledge_base.list_entries(limit=1000)
        
        for other_entry in all_entries.entries:
            if other_entry.id == entry.id:
                continue
            
            # Analyze content similarity and relationship type
            relationship_info = self._analyze_content_relationship(entry, other_entry)
            
            if relationship_info:
                rel_type, strength = relationship_info
                if strength >= 0.3:  # Minimum threshold
                    relationships.append((other_entry.id, rel_type, strength))
        
        # Sort by strength and return top relationships
        relationships.sort(key=lambda x: x[2], reverse=True)
        return relationships[:10]  # Limit to top 10
    
    def _analyze_content_relationship(self, entry1: KnowledgeEntry, 
                                    entry2: KnowledgeEntry) -> Optional[Tuple[str, float]]:
        """
        Analyze relationship between two entries based on content
        
        Args:
            entry1: First entry
            entry2: Second entry
            
        Returns:
            Tuple of (relationship_type, strength) or None
        """
        content1 = f"{entry1.title} {entry1.content}".lower()
        content2 = f"{entry2.title} {entry2.content}".lower()
        
        # Check for explicit relationship keywords
        for rel_type, keywords in self.relationship_keywords.items():
            for keyword in keywords:
                if keyword in content1 and any(word in content2.split() for word in entry2.title.lower().split()):
                    return (rel_type, 0.8)
                if keyword in content2 and any(word in content1.split() for word in entry1.title.lower().split()):
                    return (rel_type, 0.8)
        
        # Calculate text similarity
        similarity = SequenceMatcher(None, content1, content2).ratio()
        
        if similarity >= 0.3:
            return ('similar_to', similarity)
        elif similarity >= 0.2:
            return ('related_to', similarity * 0.8)
        
        return None
    
    def detect_tag_relationships(self, entry: KnowledgeEntry) -> List[Tuple[str, str, float]]:
        """
        Detect relationships based on tag overlap
        
        Args:
            entry: KnowledgeEntry to analyze
            
        Returns:
            List of (target_entry_id, relationship_type, strength) tuples
        """
        if not entry.tags:
            return []
        
        relationships = []
        entry_tags = set(tag.lower() for tag in entry.tags)
        
        # Get entries with overlapping tags
        all_entries = self.knowledge_base.list_entries(limit=1000)
        
        for other_entry in all_entries.entries:
            if other_entry.id == entry.id or not other_entry.tags:
                continue
            
            other_tags = set(tag.lower() for tag in other_entry.tags)
            common_tags = entry_tags & other_tags
            
            if common_tags:
                # Calculate relationship strength based on tag overlap
                overlap_ratio = len(common_tags) / len(entry_tags | other_tags)
                
                if overlap_ratio >= 0.5:
                    relationships.append((other_entry.id, 'similar_to', overlap_ratio))
                elif overlap_ratio >= 0.3:
                    relationships.append((other_entry.id, 'related_to', overlap_ratio * 0.8))
        
        return relationships
    
    def detect_category_relationships(self, entry: KnowledgeEntry) -> List[Tuple[str, str, float]]:
        """
        Detect relationships based on category similarity
        
        Args:
            entry: KnowledgeEntry to analyze
            
        Returns:
            List of (target_entry_id, relationship_type, strength) tuples
        """
        relationships = []
        
        # Get entries in the same category
        same_category_entries = self.knowledge_base.list_entries(
            category=entry.category, 
            limit=50
        )
        
        for other_entry in same_category_entries.entries:
            if other_entry.id == entry.id:
                continue
            
            # Entries in same category are related
            relationships.append((other_entry.id, 'related_to', 0.6))
        
        return relationships
    
    def calculate_relationship_strength(self, source: KnowledgeEntry, 
                                      target: KnowledgeEntry) -> float:
        """
        Calculate overall relationship strength between two entries
        
        Args:
            source: Source entry
            target: Target entry
            
        Returns:
            Relationship strength (0.0-1.0)
        """
        strength_factors = []
        
        # Content similarity
        content_rel = self._analyze_content_relationship(source, target)
        if content_rel:
            strength_factors.append(content_rel[1])
        
        # Tag overlap
        if source.tags and target.tags:
            source_tags = set(tag.lower() for tag in source.tags)
            target_tags = set(tag.lower() for tag in target.tags)
            common_tags = source_tags & target_tags
            
            if common_tags:
                tag_strength = len(common_tags) / len(source_tags | target_tags)
                strength_factors.append(tag_strength)
        
        # Category similarity
        if source.category == target.category:
            strength_factors.append(0.4)
        
        # Title similarity
        title_similarity = SequenceMatcher(
            None, 
            source.title.lower(), 
            target.title.lower()
        ).ratio()
        
        if title_similarity >= 0.3:
            strength_factors.append(title_similarity)
        
        # Calculate weighted average
        if strength_factors:
            return sum(strength_factors) / len(strength_factors)
        else:
            return 0.0
    
    def suggest_relationship_type(self, source: KnowledgeEntry, 
                                 target: KnowledgeEntry) -> str:
        """
        Suggest the most appropriate relationship type between two entries
        
        Args:
            source: Source entry
            target: Target entry
            
        Returns:
            Suggested relationship type
        """
        source_content = f"{source.title} {source.content}".lower()
        target_content = f"{target.title} {target.content}".lower()
        
        # Check for explicit relationship indicators
        for rel_type, keywords in self.relationship_keywords.items():
            for keyword in keywords:
                if keyword in source_content and target.title.lower() in source_content:
                    return rel_type
                if keyword in target_content and source.title.lower() in target_content:
                    return rel_type
        
        # Check for hierarchical relationships
        if 'part of' in source_content or 'component' in source_content:
            return 'part_of'
        
        if 'example' in source_content or 'instance' in source_content:
            return 'example_of'
        
        # Default to related_to for general relationships
        return 'related_to'
    
    def analyze_entry_relationships(self, entry: KnowledgeEntry) -> Dict[str, List[Tuple[str, str, float]]]:
        """
        Comprehensive relationship analysis for an entry
        
        Args:
            entry: KnowledgeEntry to analyze
            
        Returns:
            Dictionary with relationship analysis results
        """
        results = {
            'content_relationships': self.detect_content_relationships(entry),
            'tag_relationships': self.detect_tag_relationships(entry),
            'category_relationships': self.detect_category_relationships(entry)
        }
        
        # Combine and deduplicate relationships
        all_relationships = {}
        
        for rel_type, relationships in results.items():
            for target_id, relationship_type, strength in relationships:
                key = (target_id, relationship_type)
                
                if key not in all_relationships:
                    all_relationships[key] = []
                
                all_relationships[key].append((rel_type, strength))
        
        # Calculate final relationship strengths
        final_relationships = []
        
        for (target_id, relationship_type), sources in all_relationships.items():
            # Average the strengths from different sources
            avg_strength = sum(strength for _, strength in sources) / len(sources)
            
            # Boost strength if detected by multiple methods
            if len(sources) > 1:
                avg_strength = min(1.0, avg_strength * 1.2)
            
            final_relationships.append((target_id, relationship_type, avg_strength))
        
        # Sort by strength
        final_relationships.sort(key=lambda x: x[2], reverse=True)
        
        results['combined_relationships'] = final_relationships
        
        return results
    
    def find_potential_contradictions(self, entry: KnowledgeEntry) -> List[Tuple[str, float]]:
        """
        Find entries that might contradict the given entry
        
        Args:
            entry: KnowledgeEntry to check for contradictions
            
        Returns:
            List of (entry_id, confidence) tuples for potential contradictions
        """
        contradictions = []
        contradiction_keywords = [
            'not', 'never', 'incorrect', 'wrong', 'false', 'myth', 
            'misconception', 'however', 'but', 'although', 'despite'
        ]
        
        entry_content = entry.content.lower()
        entry_title = entry.title.lower()
        
        # Get entries in same category for comparison
        same_category = self.knowledge_base.list_entries(
            category=entry.category, 
            limit=100
        )
        
        for other_entry in same_category.entries:
            if other_entry.id == entry.id:
                continue
            
            other_content = other_entry.content.lower()
            other_title = other_entry.title.lower()
            
            # Check for contradiction indicators
            contradiction_score = 0.0
            
            # Look for negation patterns
            for keyword in contradiction_keywords:
                if keyword in other_content:
                    # Check if the negation relates to our entry's topic
                    entry_words = set(entry_title.split())
                    if any(word in other_content for word in entry_words if len(word) > 3):
                        contradiction_score += 0.3
            
            # Check for opposing statements
            if 'not' in other_content and any(word in other_content for word in entry_title.split() if len(word) > 3):
                contradiction_score += 0.4
            
            if contradiction_score >= 0.3:
                contradictions.append((other_entry.id, contradiction_score))
        
        return contradictions
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about relationships in the knowledge base
        
        Returns:
            Dictionary with relationship statistics
        """
        stats = {
            'total_relationships': 0,
            'relationship_types': Counter(),
            'avg_relationships_per_entry': 0.0,
            'most_connected_entries': []
        }
        
        try:
            import sqlite3
            
            with sqlite3.connect(self.knowledge_base.db_path) as conn:
                cursor = conn.cursor()
                
                # Count total relationships
                cursor.execute('SELECT COUNT(*) FROM knowledge_relationships')
                stats['total_relationships'] = cursor.fetchone()[0]
                
                # Count by relationship type
                cursor.execute('''
                    SELECT relationship_type, COUNT(*) 
                    FROM knowledge_relationships 
                    GROUP BY relationship_type
                ''')
                
                for rel_type, count in cursor.fetchall():
                    stats['relationship_types'][rel_type] = count
                
                # Calculate average relationships per entry
                cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
                total_entries = cursor.fetchone()[0]
                
                if total_entries > 0:
                    stats['avg_relationships_per_entry'] = stats['total_relationships'] / total_entries
                
                # Find most connected entries
                cursor.execute('''
                    SELECT e.id, e.title, e.connection_count
                    FROM knowledge_entries e
                    WHERE e.connection_count > 0
                    ORDER BY e.connection_count DESC
                    LIMIT 10
                ''')
                
                stats['most_connected_entries'] = [
                    {'id': row[0], 'title': row[1], 'connections': row[2]}
                    for row in cursor.fetchall()
                ]
                
        except Exception as e:
            print(f"Error getting relationship statistics: {e}")
        
        return stats
