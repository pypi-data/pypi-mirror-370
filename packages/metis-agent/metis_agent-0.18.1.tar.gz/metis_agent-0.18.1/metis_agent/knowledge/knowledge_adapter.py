"""
Knowledge Base Adapter

Integrates the knowledge base system with the existing memory architecture,
providing seamless integration between SQLite memory, Titans memory, and
the knowledge base.
"""

import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from .knowledge_base import KnowledgeBase
from .knowledge_config import KnowledgeConfig
from .knowledge_entry import KnowledgeEntry, KnowledgeQueryResult


class KnowledgeAdapter:
    """
    Adapter to integrate knowledge base with Metis Agent memory system
    """
    
    def __init__(self, agent, knowledge_config: Optional[KnowledgeConfig] = None):
        """
        Initialize the knowledge adapter
        
        Args:
            agent: Agent instance
            knowledge_config: Knowledge configuration (if None, creates default)
        """
        self.agent = agent
        
        # Initialize knowledge configuration
        if knowledge_config is None:
            # Use agent's knowledge directory if available
            knowledge_dir = "knowledge"
            if hasattr(agent, 'config') and agent.config:
                # Try to get knowledge directory from agent config
                knowledge_dir = getattr(agent.config, 'knowledge_dir', 'knowledge')
            
            knowledge_config = KnowledgeConfig(knowledge_dir)
        
        self.config = knowledge_config
        
        # Initialize knowledge base
        self.knowledge_base = KnowledgeBase(knowledge_config)
        
        # Performance metrics
        self.performance_metrics = {
            "queries_processed": 0,
            "knowledge_retrieved": 0,
            "ai_entries_created": 0,
            "average_relevance": 0.0
        }
        
        print("+ Knowledge base adapter initialized")
    
    def get_knowledge_context(self, query: str, session_id: Optional[str] = None, 
                              max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge base entries for context enhancement
        
        Args:
            query: User query
            session_id: Session identifier
            max_results: Maximum number of knowledge entries to return
            
        Returns:
            List of knowledge entries formatted for memory integration
        """
        try:
            # Search knowledge base
            kb_results = self.knowledge_base.search(
                query=query,
                max_results=max_results,
                similarity_threshold=self.config.similarity_threshold
            )
            
            # Convert to memory format compatible with existing system
            knowledge_memories = []
            for i, entry in enumerate(kb_results.entries):
                relevance_score = kb_results.relevance_scores[i] if i < len(kb_results.relevance_scores) else 1.0
                
                knowledge_memories.append({
                    "content": f"{entry.title}: {entry.get_summary(400)}",
                    "memory_type": f"knowledge_{entry.category}",
                    "relevance_score": relevance_score,
                    "source": "knowledge_base",
                    "category": entry.category,
                    "tags": entry.tags,
                    "entry_id": entry.id,
                    "timestamp": entry.updated_at.timestamp()
                })
            
            # Update metrics
            self.performance_metrics["queries_processed"] += 1
            self.performance_metrics["knowledge_retrieved"] += len(knowledge_memories)
            
            if knowledge_memories:
                avg_relevance = sum(mem["relevance_score"] for mem in knowledge_memories) / len(knowledge_memories)
                total_queries = self.performance_metrics["queries_processed"]
                current_avg = self.performance_metrics["average_relevance"]
                self.performance_metrics["average_relevance"] = (
                    (current_avg * (total_queries - 1) + avg_relevance) / total_queries
                )
            
            return knowledge_memories
            
        except Exception as e:
            print(f"⚠️ Error retrieving knowledge context: {e}")
            return []
    
    def store_ai_insight(self, content: str, title: str = None, 
                         category: str = "ai_insights", tags: List[str] = None,
                         session_id: Optional[str] = None) -> Optional[KnowledgeEntry]:
        """
        Store AI-generated insights in the knowledge base
        
        Args:
            content: The insight content
            title: Title for the insight (auto-generated if None)
            category: Category for the insight
            tags: Tags to associate with the insight
            session_id: Session identifier
            
        Returns:
            Created KnowledgeEntry or None if failed
        """
        try:
            # Auto-generate title if not provided
            if not title:
                # Extract first sentence or first 50 characters
                first_sentence = content.split('.')[0]
                if len(first_sentence) > 50:
                    title = content[:47] + "..."
                else:
                    title = first_sentence
            
            # Create knowledge entry
            import uuid
            entry = KnowledgeEntry(
                id=f"ai_{uuid.uuid4().hex[:8]}",
                title=title,
                content=content,
                category=category,
                tags=tags or [],
                source="ai_generated",
                metadata={
                    "session_id": session_id,
                    "generated_at": datetime.now().isoformat(),
                    "agent_version": getattr(self.agent, 'version', 'unknown')
                }
            )
            
            # Store in knowledge base
            if self.knowledge_base.store(entry):
                self.performance_metrics["ai_entries_created"] += 1
                return entry
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Error storing AI insight: {e}")
            return None
    
    def analyze_conversation_for_insights(self, conversation_history: List[Dict[str, Any]]) -> List[str]:
        """
        Analyze conversation history to extract potential insights
        
        Args:
            conversation_history: List of conversation entries
            
        Returns:
            List of insight strings to be stored
        """
        insights = []
        
        try:
            # Look for patterns in conversation
            user_preferences = []
            technical_topics = []
            repeated_questions = []
            
            for entry in conversation_history:
                content = entry.get('content', '').lower()
                
                # Detect user preferences
                if any(phrase in content for phrase in ['i prefer', 'i like', 'i want', 'i need']):
                    user_preferences.append(content)
                
                # Detect technical topics
                if any(term in content for term in ['python', 'javascript', 'api', 'database', 'code', 'programming']):
                    technical_topics.append(content)
                
                # Detect repeated questions (simplified)
                if content.endswith('?') and len(content) > 10:
                    repeated_questions.append(content)
            
            # Generate insights
            if user_preferences:
                insights.append(f"User Preferences: {'; '.join(user_preferences[:3])}")
            
            if technical_topics:
                insights.append(f"Technical Interests: Focus on {', '.join(set(technical_topics[:5]))}")
            
            if len(repeated_questions) > 2:
                insights.append(f"Common Questions: User frequently asks about similar topics")
            
        except Exception as e:
            print(f"⚠️ Error analyzing conversation: {e}")
        
        return insights
    
    def import_knowledge_from_directory(self, directory_path: str, 
                                        category: str = None, recursive: bool = False) -> List[KnowledgeEntry]:
        """
        Import knowledge from a directory of files
        
        Args:
            directory_path: Path to directory containing knowledge files
            category: Category to assign to imported entries
            recursive: Whether to search subdirectories
            
        Returns:
            List of imported KnowledgeEntry objects
        """
        imported_entries = []
        
        try:
            if not os.path.exists(directory_path):
                print(f"Directory not found: {directory_path}")
                return imported_entries
            
            # Supported file extensions
            supported_extensions = ['.md', '.txt', '.markdown']
            
            # Walk directory
            if recursive:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in supported_extensions):
                            file_path = os.path.join(root, file)
                            
                            # Determine category from subdirectory if not provided
                            file_category = category
                            if not file_category:
                                rel_path = os.path.relpath(root, directory_path)
                                if rel_path != '.':
                                    file_category = rel_path.split(os.sep)[0]
                                else:
                                    file_category = "imported"
                            
                            entry = self.knowledge_base.import_from_file(file_path, file_category)
                            if entry:
                                imported_entries.append(entry)
            else:
                # Non-recursive import
                for file in os.listdir(directory_path):
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        file_path = os.path.join(directory_path, file)
                        if os.path.isfile(file_path):
                            entry = self.knowledge_base.import_from_file(
                                file_path, 
                                category or "imported"
                            )
                            if entry:
                                imported_entries.append(entry)
            
            print(f"+ Imported {len(imported_entries)} knowledge entries from {directory_path}")
            
        except Exception as e:
            print(f"⚠️ Error importing from directory {directory_path}: {e}")
        
        return imported_entries
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base statistics"""
        kb_stats = self.knowledge_base.get_statistics()
        
        return {
            "knowledge_base": kb_stats,
            "adapter_metrics": self.performance_metrics,
            "configuration": {
                "enabled": self.config.enabled,
                "auto_learning": self.config.auto_learning,
                "max_context_entries": self.config.max_context_entries,
                "similarity_threshold": self.config.similarity_threshold,
                "external_provider": self.config.external_provider
            },
            "categories": list(self.config.categories.keys()),
            "enabled_modules": self.config.get_enabled_modules()
        }
    
    def search_knowledge(self, query: str, **kwargs) -> KnowledgeQueryResult:
        """
        Search knowledge base with optional filters
        
        Args:
            query: Search query
            **kwargs: Additional search parameters (category, tags, max_results, etc.)
            
        Returns:
            KnowledgeQueryResult with matching entries
        """
        return self.knowledge_base.search(query, **kwargs)
    
    def create_knowledge_entry(self, title: str, content: str, category: str,
                               tags: List[str] = None) -> Optional[KnowledgeEntry]:
        """
        Create a new knowledge entry
        
        Args:
            title: Entry title
            content: Entry content
            category: Entry category
            tags: Entry tags
            
        Returns:
            Created KnowledgeEntry or None if failed
        """
        try:
            import uuid
            entry = KnowledgeEntry(
                id=f"kb_{uuid.uuid4().hex[:8]}",
                title=title,
                content=content,
                category=category,
                tags=tags or [],
                source="user_input"
            )
            
            if self.knowledge_base.store(entry):
                return entry
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Error creating knowledge entry: {e}")
            return None
    
    def update_knowledge_entry(self, entry_id: str, title: str = None, 
                               content: str = None, tags: List[str] = None) -> bool:
        """
        Update an existing knowledge entry
        
        Args:
            entry_id: ID of entry to update
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            entry = self.knowledge_base.get(entry_id)
            if not entry:
                return False
            
            # Update fields if provided
            if title is not None:
                entry.title = title
            if content is not None:
                entry.content = content
            if tags is not None:
                entry.tags = tags
            
            # Update timestamp and version
            entry.updated_at = datetime.now()
            entry.version += 1
            
            return self.knowledge_base.update(entry)
            
        except Exception as e:
            print(f"⚠️ Error updating knowledge entry: {e}")
            return False
    
    def delete_knowledge_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry"""
        return self.knowledge_base.delete(entry_id)
    
    def list_knowledge_entries(self, category: str = None, tags: List[str] = None,
                               limit: int = 50) -> List[KnowledgeEntry]:
        """List knowledge entries with optional filtering"""
        return self.knowledge_base.list_entries(category, tags, limit)
    
    def export_knowledge_entry(self, entry_id: str, file_path: str, 
                               format: str = 'md') -> bool:
        """Export a knowledge entry to file"""
        return self.knowledge_base.export_to_file(entry_id, file_path, format)
    
    def get_categories(self) -> List[str]:
        """Get all categories in use"""
        return self.knowledge_base.get_categories()
    
    def get_tags(self) -> List[str]:
        """Get all tags in use"""
        return self.knowledge_base.get_tags()
