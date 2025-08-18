"""
Titans Memory Adapter for Metis Agent Integration

This module provides an adapter to integrate the Titans-inspired memory system
with the Metis Agent architecture.
"""

import os
import time
from typing import Dict, Any, List, Optional, Union
from .titans_memory import TitansInspiredMemory

class TitansMemoryAdapter:
    """
    Adapter to integrate Titans memory with Metis Agent
    """
    
    def __init__(self, agent, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter
        
        Args:
            agent: Agent instance
            config: Configuration dict with optional parameters
        """
        self.agent = agent
        self.config = config or {}
        
        # Initialize Titans memory with configuration
        # Use a stable memory directory that doesn't depend on current working directory
        # First try the package directory, then fall back to user home directory
        try:
            # Try to use package directory
            package_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            memory_dir = os.path.join(package_dir, "memory", "titans")
        except:
            # Fall back to user home directory if package directory isn't writable
            import tempfile
            memory_dir = os.path.join(tempfile.gettempdir(), "metis_agent", "memory", "titans")
        
        os.makedirs(memory_dir, exist_ok=True)
        
        self.titans_memory = TitansInspiredMemory(
            memory_dir=memory_dir,
            embedding_dim=self.config.get("embedding_dim", 128),
            surprise_threshold=self.config.get("surprise_threshold", 0.7),
            chunk_size=self.config.get("chunk_size", 3),
            short_term_capacity=self.config.get("short_term_capacity", 15),
            long_term_capacity=self.config.get("long_term_capacity", 1000)
        )
        
        # Load existing state
        self.titans_memory.load_state()
        
        # Track performance metrics
        self.performance_metrics = {
            "queries_processed": 0,
            "memories_stored": 0,
            "adaptations_triggered": 0,
            "average_surprise": 0.0
        }
        
        print("+ Titans memory adapter initialized")
    
    def enhance_query_processing(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced query processing with comprehensive error handling and SQLite integration
        
        Args:
            query: User query
            session_id: Session identifier
            
        Returns:
            Enhanced query data
        """
        try:
            # Store the incoming query
            context = f"session_{session_id}" if session_id else "default_session"
            
            storage_info = self.titans_memory.store_memory(
                content=query,
                context=context,
                metadata={
                    "type": "user_query",
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            )
            
            # Get relevant memories from Titans memory (reduced for token limits)
            relevant_memories = self.titans_memory.retrieve_relevant_memories(query, max_results=2)
            
            # Get SQLite conversation history for enhanced context (reduced for token limits)
            sqlite_memories = self._get_sqlite_conversation_history(query, session_id, max_results=3)
            
            # Get knowledge base context if available (reduced for token limits)
            knowledge_memories = self._get_knowledge_base_context(query, session_id, max_results=2)
            
            # Combine memories: prioritize recent conversation history for better turn-by-turn continuity
            # Order: SQLite conversation history first, then Titans semantic, then knowledge base
            combined_memories = sqlite_memories + relevant_memories + knowledge_memories
            
            # Get attention context
            attention_context = self.titans_memory.get_attention_context(query)
            
            # Update performance metrics safely
            self._update_metrics_safely(storage_info)
            
            return {
                "original_query": query,
                "enhanced_context": self._build_memory_context(combined_memories),
                "storage_info": storage_info,
                "relevant_memories": combined_memories,
                "knowledge_entries": knowledge_memories,  # Add knowledge entries separately
                "attention_metadata": {
                    "num_contexts": attention_context.get("num_contexts", 0),
                    "context_sources": attention_context.get("context_sources", [])
                }
            }
            
        except Exception as e:
            print(f"⚠️ Error in Titans memory enhancement: {e}")
            # Return safe fallback with SQLite memories if available
            try:
                sqlite_memories = self._get_sqlite_conversation_history(query, session_id, max_results=3)
                fallback_context = self._build_memory_context(sqlite_memories)
            except:
                sqlite_memories = []
                fallback_context = ""
                
            return {
                "original_query": query,
                "enhanced_context": fallback_context,
                "storage_info": None,
                "relevant_memories": sqlite_memories,
                "knowledge_entries": [],  # Empty knowledge entries on error
                "error": str(e),
                "attention_metadata": {"num_contexts": 0, "context_sources": []}
            }
            
    def _update_metrics_safely(self, storage_info: Dict[str, Any]) -> None:
        """
        Safely update performance metrics
        
        Args:
            storage_info: Storage information from store_memory
        """
        try:
            self.performance_metrics["queries_processed"] += 1
            if storage_info.get("stored_long_term"):
                self.performance_metrics["memories_stored"] += 1
            if storage_info.get("triggered_adaptation"):
                self.performance_metrics["adaptations_triggered"] += 1
            
            # Calculate running average surprise safely
            total_queries = self.performance_metrics["queries_processed"]
            current_avg = self.performance_metrics.get("average_surprise", 0.0)
            new_surprise = storage_info.get("surprise_score", 0.0)
            
            if total_queries > 0:
                self.performance_metrics["average_surprise"] = (
                    (current_avg * (total_queries - 1) + new_surprise) / total_queries
                )
        except Exception as e:
            print(f"⚠️ Error updating metrics: {e}")
    
    def store_response(self, query: str, response: Any, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store agent response in Titans memory with error handling
        
        Args:
            query: User query
            response: Agent response
            session_id: Session identifier
            
        Returns:
            Storage info
        """
        try:
            if not response:
                return {"stored": False, "reason": "empty_response"}
            
            # Extract content from different response formats
            content = ""
            if isinstance(response, dict):
                if "content" in response:
                    content = str(response["content"])
                elif "summary" in response:
                    content = str(response["summary"])
                elif "answer" in response:
                    content = str(response["answer"])
                else:
                    content = str(response)
            else:
                content = str(response)
            
            if not content.strip():
                return {"stored": False, "reason": "empty_content"}
                
            context = f"response_to_session_{session_id}" if session_id else "response_context"
            
            storage_info = self.titans_memory.store_memory(
                content=content,
                context=context,
                metadata={
                    "type": "agent_response",
                    "original_query": query,
                    "session_id": session_id,
                    "timestamp": time.time()
                }
            )
            
            return storage_info
            
        except Exception as e:
            print(f"⚠️ Error storing response in Titans memory: {e}")
            return {"stored": False, "error": str(e)}
    
    def _get_sqlite_conversation_history(self, query: str, session_id: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant conversation history from SQLite memory database
        
        Args:
            query: Current user query for relevance matching
            session_id: Session identifier
            max_results: Maximum number of memories to return
            
        Returns:
            List of memory dictionaries compatible with Titans format
        """
        try:
            import sqlite3
            import os
            from difflib import SequenceMatcher
            
            # Get the SQLite memory database path from agent
            if hasattr(self.agent, 'memory_path'):
                db_path = self.agent.memory_path
            else:
                # Fallback to default location
                memory_dir = os.path.join(os.getcwd(), "memory")
                db_path = os.path.join(memory_dir, "memory.db")
            
            if not os.path.exists(db_path):
                return []
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get recent conversation history, prioritizing current session
            if session_id:
                # First try to get from current session
                cursor.execute(
                    "SELECT content FROM user_inputs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (session_id, max_results * 2)
                )
                session_inputs = cursor.fetchall()
                
                cursor.execute(
                    "SELECT content FROM agent_outputs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (session_id, max_results * 2)
                )
                session_outputs = cursor.fetchall()
            else:
                session_inputs = []
                session_outputs = []
            
            # Get general recent history if we need more context
            remaining_slots = max_results - len(session_inputs)
            if remaining_slots > 0:
                cursor.execute(
                    "SELECT content FROM user_inputs ORDER BY timestamp DESC LIMIT ?",
                    (remaining_slots * 2,)
                )
                general_inputs = cursor.fetchall()
            else:
                general_inputs = []
            
            conn.close()
            
            # Combine and process memories
            all_contents = []
            
            # Add session-specific inputs with similarity scoring
            for row in session_inputs:
                content = row[0]
                if content and content.strip():
                    # Even session data should have semantic relevance
                    similarity_score = SequenceMatcher(None, query.lower(), content.lower()).ratio()
                    session_boost = 0.3  # Boost for being in same session
                    combined_score = min(1.0, similarity_score + session_boost)
                    
                    # Only include session memories if they have some relevance
                    if combined_score > 0.5:  # Higher threshold for inclusion
                        all_contents.append((content, "user_input", combined_score))
            
            # Add session-specific outputs
            for row in session_outputs:
                content = row[0]
                if content and content.strip() and len(content) < 500:  # Avoid very long responses
                    all_contents.append((content, "agent_response", 0.8))
            
            # Add general inputs if needed with semantic similarity scoring
            for i, row in enumerate(general_inputs):
                content = row[0]
                if content and content.strip():
                    # Calculate semantic similarity with current query
                    similarity_score = SequenceMatcher(None, query.lower(), content.lower()).ratio()
                    
                    # Only include memories with reasonable similarity (> 0.3) or very recent ones
                    recency_boost = max(0.1, 0.5 - (i * 0.05))  # Small recency boost
                    combined_score = max(similarity_score, recency_boost)
                    
                    # Only add if there's meaningful similarity or it's very recent
                    if combined_score > 0.4 or i < 2:  # High similarity OR very recent
                        all_contents.append((content, "user_input", combined_score))
            
            # Convert to Titans memory format
            sqlite_memories = []
            for content, memory_type, relevance in all_contents[:max_results]:
                sqlite_memories.append({
                    "content": content,
                    "memory_type": f"sqlite_{memory_type}",
                    "relevance_score": relevance,
                    "source": "sqlite_db",
                    "timestamp": time.time()
                })
            
            return sqlite_memories
            
        except Exception as e:
            print(f"⚠️ Error retrieving SQLite conversation history: {e}")
            return []
    
    def _build_memory_context(self, relevant_memories: List[Dict[str, Any]], max_tokens: int = 1000) -> str:
        """
        Build enhanced context string from relevant memories with token limit
        
        Args:
            relevant_memories: List of relevant memory entries
            max_tokens: Maximum tokens for context (approximate)
        
        Returns:
            Context string
        """
        if not relevant_memories:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, memory in enumerate(relevant_memories, 1):
            relevance = memory["relevance_score"]
            content = memory["content"]
            memory_type = memory["memory_type"]
            
            # Format memory entry more naturally without metadata
            entry = content
            
            # Rough token estimation (4 chars ≈ 1 token)
            entry_tokens = len(entry) // 4
            
            # Check if adding this entry would exceed token limit
            if current_length // 4 + entry_tokens > max_tokens:
                context_parts.append(f"... (truncated {len(relevant_memories) - i + 1} more entries to stay within token limits)")
                break
            
            context_parts.append(entry)
            current_length += len(entry)
        
        return "\n".join(context_parts) + "\n"
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive insights about adaptive memory performance
        
        Returns:
            Dictionary with insights
        """
        memory_stats = self.titans_memory.get_memory_stats()
        
        insights = {
            "performance_metrics": self.performance_metrics.copy(),
            "memory_statistics": memory_stats,
            "health_indicators": {
                "memory_utilization": memory_stats["short_term_count"] / self.titans_memory.short_term_memory.maxlen,
                "adaptation_rate": memory_stats["adaptation_count"] / max(1, self.performance_metrics["queries_processed"]),
                "surprise_level": "high" if self.performance_metrics["average_surprise"] > self.titans_memory.surprise_threshold else "normal",
                "learning_active": memory_stats["adaptation_count"] > 0
            },
            "recommendations": self._generate_recommendations(memory_stats)
        }
        
        return insights
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on memory performance
        
        Args:
            stats: Memory statistics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if stats["adaptation_count"] == 0:
            recommendations.append("Consider lowering surprise_threshold to enable more learning")
        
        if stats["avg_surprise_recent"] > 1.5:
            recommendations.append("High surprise levels detected - agent is encountering novel content")
        
        if stats["short_term_count"] < 5:
            recommendations.append("Low short-term memory usage - increase interaction frequency")
        
        if stats["long_term_count"] > 800:
            recommendations.append("Long-term memory approaching capacity - consider periodic cleanup")
        
        return recommendations
    
    def save_state(self) -> None:
        """Save the adaptive memory state"""
        self.titans_memory.save_state()
    
    def configure(self, **kwargs) -> None:
        """
        Dynamically configure the memory system
        
        Available options:
        - surprise_threshold: float (0.1 to 2.0)
        - chunk_size: int (1 to 10)
        """
        if "surprise_threshold" in kwargs:
            threshold = max(0.1, min(2.0, float(kwargs["surprise_threshold"])))
            self.titans_memory.surprise_threshold = threshold
            print(f"🎛️ Updated surprise threshold to {threshold}")
        
        if "chunk_size" in kwargs:
            chunk_size = max(1, min(10, int(kwargs["chunk_size"])))
            self.titans_memory.chunk_size = chunk_size
            print(f"🎛️ Updated chunk size to {chunk_size}")
    
    def _get_knowledge_base_context(self, query: str, session_id: Optional[str] = None, 
                                   max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Get relevant knowledge base entries for context enhancement
        
        Args:
            query: User query
            session_id: Session identifier
            max_results: Maximum number of knowledge entries to return
            
        Returns:
            List of knowledge entries formatted for memory integration
        """
        try:
            # Skip knowledge base for simple conversational queries to improve turn-by-turn continuity
            # Only skip for very basic conversational patterns, not informational queries
            basic_conversational_patterns = [
                'yes', 'no', 'ok', 'okay', 'thanks', 'thank you',
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                'nice', 'great', 'awesome', 'cool', 'perfect',
                'i think so', 'i believe so', 'i agree', 'i disagree'
            ]
            
            # Very short responses that are clearly conversational
            short_responses = [
                'yes', 'no', 'ok', 'okay', 'sure', 'fine', 'good', 'bad',
                'thanks', 'hi', 'hey', 'hello', 'bye', 'goodbye'
            ]
            
            query_lower = query.lower().strip()
            
            # Only skip knowledge base for:
            # 1. Very short conversational responses (1-2 words)
            # 2. Exact matches to basic conversational patterns
            if (query_lower in short_responses or 
                any(query_lower == pattern for pattern in basic_conversational_patterns) or
                (len(query_lower.split()) <= 2 and any(pattern in query_lower for pattern in short_responses))):
                return []
            
            # Check if agent has knowledge base enabled
            if not hasattr(self.agent, 'config') or not self.agent.config:
                return []
            
            if not self.agent.config.is_knowledge_enabled():
                return []
            
            # Import knowledge components
            from ...knowledge.knowledge_config import KnowledgeConfig
            from ...knowledge.knowledge_adapter import KnowledgeAdapter
            
            # Initialize knowledge base
            knowledge_dir = self.agent.config.get_knowledge_dir()
            config = KnowledgeConfig(knowledge_dir)
            
            # Use agent's knowledge similarity threshold if available
            if hasattr(self.agent.config, 'get_knowledge_similarity_threshold'):
                config.similarity_threshold = self.agent.config.get_knowledge_similarity_threshold()
            
            # Create adapter
            adapter = KnowledgeAdapter(self.agent, config)
            
            # Get knowledge context
            knowledge_memories = adapter.get_knowledge_context(
                query=query,
                session_id=session_id,
                max_results=max_results
            )
            
            return knowledge_memories
            
        except Exception as e:
            print(f"⚠️ Error retrieving knowledge base context: {e}")
            return []