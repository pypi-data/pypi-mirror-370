"""
Titans-Inspired Adaptive Memory System for Metis Agent

This module implements an adaptive memory system inspired by the Titans approach,
providing lightweight embedding, short-term and long-term memory, surprise detection,
and attentional context mechanisms without requiring PyTorch.
"""

import os
import time
import json
import numpy as np
import pickle
import hashlib
from dataclasses import dataclass, field, asdict
from collections import deque
from typing import Dict, List, Any, Optional, Tuple, Set
import re


@dataclass
class MemoryEntry:
    """A single memory entry in the adaptive memory system"""
    content: str
    context: str
    embedding: np.ndarray
    timestamp: float
    memory_type: str = "standard"  # standard, insight, pattern
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    relevance_boost: float = 0.0
    surprise_score: float = 0.0
    id: Optional[str] = None


@dataclass
class AdaptiveMemoryState:
    """State of the adaptive memory system for serialization"""
    short_term_memory: List[Dict[str, Any]]
    long_term_memory: List[Dict[str, Any]]
    context_embeddings: Dict[str, List[float]]
    context_frequencies: Dict[str, int]
    adaptation_count: int
    last_adaptation_time: float
    avg_surprise_recent: float
    embedding_dim: int
    surprise_threshold: float
    chunk_size: int
    

class LightweightEmbedding:
    """
    Lightweight text embedding implementation using TF-IDF inspired approach
    """
    
    def __init__(self, embedding_dim: int = 128):
        """Initialize the embedding system"""
        self.embedding_dim = embedding_dim
        self.vocab = {}  # word -> index mapping
        self.vocab_size = 0
        self.word_weights = {}  # word -> weight mapping
        
        # Create deterministic random projection matrix
        np.random.seed(42)  # Fixed seed for reproducibility
        self.projection_matrix = np.random.normal(
            size=(10000, embedding_dim)  # Large enough for most vocabularies
        )
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization function"""
        # Convert to lowercase and split on non-alphanumeric characters
        text = text.lower()
        # Remove punctuation and split
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _update_vocab(self, tokens: List[str]):
        """Update vocabulary with new tokens"""
        for token in tokens:
            if token not in self.vocab:
                self.vocab[token] = self.vocab_size
                self.vocab_size += 1
                
                # Initialize word weight (simple IDF-like approach)
                self.word_weights[token] = 1.0
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text to embedding vector"""
        if not text:
            # Return zero vector for empty text
            return np.zeros(self.embedding_dim)
            
        tokens = self._tokenize(text)
        self._update_vocab(tokens)
        
        # Create token frequency dict (TF-like approach)
        token_counts = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1
        
        # Create weighted vector
        embedding = np.zeros(self.embedding_dim)
        
        for token, count in token_counts.items():
            if token in self.vocab:
                # Get token index and weight
                idx = self.vocab[token] % self.projection_matrix.shape[0]
                weight = count * self.word_weights[token]
                
                # Add to embedding with weight
                embedding += weight * self.projection_matrix[idx]
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        if np.all(embedding1 == 0) or np.all(embedding2 == 0):
            return 0.0
            
        similarity = np.dot(embedding1, embedding2)
        return max(0.0, min(1.0, float(similarity)))  # Ensure range [0, 1]
    
    def update_weights(self, text: str, importance: float = 1.0):
        """Update word weights based on importance of text"""
        tokens = self._tokenize(text)
        for token in set(tokens):  # Use set to count each token once
            if token in self.word_weights:
                # Adjust weight based on importance
                self.word_weights[token] *= (1.0 + 0.01 * importance)


class TitansInspiredMemory:
    """
    Adaptive memory system inspired by Titans approach
    """
    
    def __init__(
        self, 
        memory_dir: str,
        embedding_dim: int = 128, 
        surprise_threshold: float = 0.7,
        chunk_size: int = 3,
        short_term_capacity: int = 15,
        long_term_capacity: int = 1000
    ):
        """
        Initialize the adaptive memory system
        
        Args:
            memory_dir: Directory to store memory files
            embedding_dim: Dimension of embeddings
            surprise_threshold: Threshold for surprise detection (0.1-2.0)
            chunk_size: Number of samples to use for adaptation
            short_term_capacity: Capacity of short-term memory
            long_term_capacity: Capacity of long-term memory
        """
        self.memory_dir = memory_dir
        self.embedding_dim = embedding_dim
        self.surprise_threshold = surprise_threshold
        self.chunk_size = chunk_size
        
        # Create embedding engine
        self.embedding_engine = LightweightEmbedding(embedding_dim=embedding_dim)
        
        # Initialize memories
        self.short_term_memory = deque(maxlen=short_term_capacity)
        self.long_term_memory = []
        self.long_term_capacity = long_term_capacity
        
        # Context tracking
        self.context_embeddings = {}  # context -> embedding
        self.context_frequencies = {}  # context -> frequency
        
        # Adaptation tracking
        self.adaptation_count = 0
        self.last_adaptation_time = 0
        self.avg_surprise_recent = 0.0
        self.recent_surprises = deque(maxlen=10)
        
        # Performance optimizations
        self._embedding_cache = {}  # Cache embeddings for repeated queries
        self._similarity_cache = {}  # Cache similarity calculations
        self._max_cache_size = 1000
        self.chunk_buffer = []  # Buffer for batch updates
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        print(f"+ Titans-inspired memory initialized (dim={embedding_dim}, surprise_threshold={surprise_threshold})")
    
    def _get_cached_embedding(self, text: str) -> np.ndarray:
        """Get embedding with caching for performance"""
        # Create cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()[:16]
        
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # Generate new embedding
        embedding = self.embedding_engine.encode(text)
        
        # Cache with size limit
        if len(self._embedding_cache) < self._max_cache_size:
            self._embedding_cache[cache_key] = embedding
        
        return embedding

    def store_memory(
        self, 
        content: str, 
        context: str, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Store a new memory entry with enhanced error handling
        
        Args:
            content: Text content to store
            context: Context identifier
            metadata: Additional metadata
            
        Returns:
            Dict with storage information
        """
        try:
            if not content.strip():
                return {
                    "stored": False,
                    "reason": "empty_content",
                    "surprise_score": 0.0,
                    "triggered_adaptation": False,
                    "stored_long_term": False
                }
            
            # Create embedding with caching
            embedding = self._get_cached_embedding(content)
            
            # Calculate surprise score with error handling
            try:
                surprise_score, context_embedding = self._calculate_surprise(content, context, embedding)
            except Exception as e:
                print(f"Warning: Error calculating surprise: {e}")
                surprise_score = 0.5  # Default moderate surprise
                context_embedding = embedding.copy() if context not in self.context_embeddings else self.context_embeddings[context]
            
            # Determine memory type based on surprise
            memory_type = "standard"
            if surprise_score > self.surprise_threshold:
                memory_type = "insight"  # High surprise = new insight
            
            # Create memory entry
            entry = MemoryEntry(
                content=content,
                context=context,
                embedding=embedding,
                timestamp=time.time(),
                memory_type=memory_type,
                metadata=metadata or {},
                surprise_score=surprise_score,
                id=f"mem_{int(time.time() * 1000)}"
            )
            
            # Store in short-term memory
            self.short_term_memory.append(entry)
            
            # Update tracking data
            triggered_adaptation = False
            stored_long_term = False
            
            # Update context tracking
            if context not in self.context_frequencies:
                self.context_frequencies[context] = 1
                self.context_embeddings[context] = embedding.copy()
            else:
                self.context_frequencies[context] += 1
                # Gradually update context embedding
                alpha = 0.1  # Small update rate
                self.context_embeddings[context] = (
                    (1 - alpha) * self.context_embeddings[context] + alpha * embedding
                )
            
            # Record surprise score
            self.recent_surprises.append(surprise_score)
            self.avg_surprise_recent = sum(self.recent_surprises) / len(self.recent_surprises)
            
            # Check if adaptation should be triggered
            if len(self.short_term_memory) >= self.chunk_size:
                if self._should_adapt():
                    try:
                        self._adapt()
                        triggered_adaptation = True
                    except Exception as e:
                        print(f"Warning: Error during adaptation: {e}")
            
            # Check if should move to long-term memory
            if memory_type == "insight" or surprise_score > 1.0:
                try:
                    self._store_in_long_term(entry)
                    stored_long_term = True
                except Exception as e:
                    print(f"Warning: Error storing in long-term memory: {e}")
            
            return {
                "stored": True,
                "surprise_score": surprise_score,
                "triggered_adaptation": triggered_adaptation,
                "stored_long_term": stored_long_term,
                "memory_type": memory_type,
                "threshold": self.surprise_threshold
            }
            
        except Exception as e:
            print(f"Error: Error storing memory: {e}")
            return {
                "stored": False,
                "error": str(e),
                "surprise_score": 0.0,
                "triggered_adaptation": False,
                "stored_long_term": False,
                "threshold": self.surprise_threshold
            }
    
    def retrieve_relevant_memories(
        self, 
        query: str, 
        max_results: int = 5, 
        min_relevance: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the query with performance optimization
        
        Args:
            query: Query text
            max_results: Maximum number of results
            min_relevance: Minimum relevance score
            
        Returns:
            List of relevant memory entries
        """
        try:
            if not query.strip():
                return []
            
            # Encode query with caching
            query_embedding = self._get_cached_embedding(query)
            
            # Combine all memory sources with error handling
            all_memories = []
            
            # Add short-term memories safely
            try:
                for entry in self.short_term_memory:
                    all_memories.append(("short_term", entry))
            except Exception as e:
                print(f"Warning: Error accessing short-term memory: {e}")
            
            # Add long-term memories safely
            try:
                for entry in self.long_term_memory:
                    all_memories.append(("long_term", entry))
            except Exception as e:
                print(f"Warning: Error accessing long-term memory: {e}")
            
            if not all_memories:
                return []
            
            # Calculate similarities with error handling
            scored_memories = []
            current_time = time.time()
            
            for memory_type, entry in all_memories:
                try:
                    # Use cached similarity when possible
                    cache_key = f"{hash(query)}-{hash(str(entry.embedding))}"
                    
                    if cache_key in self._similarity_cache:
                        similarity = self._similarity_cache[cache_key]
                    else:
                        similarity = self.embedding_engine.similarity(query_embedding, entry.embedding)
                        # Cache the similarity
                        if len(self._similarity_cache) < self._max_cache_size:
                            self._similarity_cache[cache_key] = similarity
                    
                    # Apply advanced scoring with multiple factors
                    # Boost score for recent and surprising memories
                    recency_boost = 1.0 / (1.0 + (current_time - entry.timestamp) / 3600)  # Hours factor
                    surprise_boost = entry.surprise_score / 2.0
                    access_boost = min(0.2, 0.01 * entry.access_count)
                    
                    final_score = similarity + 0.2 * recency_boost + 0.1 * surprise_boost + access_boost
                    
                    scored_memories.append((final_score, memory_type, entry))
                    
                except Exception as e:
                    print(f"Warning: Error scoring memory: {e}")
                    continue
            
            # Sort by relevance and return top results
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            
            relevant_memories = []
            seen_contents = set()  # Avoid exact duplicates
            
            for score, memory_type, entry in scored_memories:
                try:
                    # Skip if below minimum relevance
                    if score < min_relevance:
                        continue
                        
                    # Skip if content is a duplicate
                    if entry.content in seen_contents:
                        continue
                        
                    # Mark content as seen
                    seen_contents.add(entry.content)
                    
                    # Increment access count for this memory
                    entry.access_count += 1
                    
                    # Adjust relevance boost based on access frequency
                    entry.relevance_boost = min(0.2, 0.01 * entry.access_count)
                    
                    # Add to results
                    relevant_memories.append({
                        "content": entry.content,
                        "context": entry.context,
                        "relevance_score": float(score),  # Ensure it's a Python float
                        "memory_type": memory_type,
                        "surprise_score": entry.surprise_score,
                        "timestamp": entry.timestamp,
                        "metadata": entry.metadata,
                        "access_count": entry.access_count
                    })
                    
                    # Stop when we have enough results
                    if len(relevant_memories) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Warning: Error formatting memory result: {e}")
                    continue
            
            return relevant_memories
            
        except Exception as e:
            print(f"Error: Error retrieving memories: {e}")
            return []
    
    def get_attention_context(self, query: str) -> Dict[str, Any]:
        """
        Get attentional context information
        
        Args:
            query: Current query
            
        Returns:
            Dict with context information
        """
        query_embedding = self.embedding_engine.encode(query)
        
        # Calculate context similarities
        context_similarities = []
        for context, embedding in self.context_embeddings.items():
            similarity = self.embedding_engine.similarity(query_embedding, embedding)
            frequency = self.context_frequencies.get(context, 0)
            
            # Combine similarity and frequency for attention score
            attention_score = similarity * (0.5 + 0.5 * min(1.0, frequency / 5.0))
            
            context_similarities.append((context, attention_score))
        
        # Sort by attention score
        context_similarities.sort(reverse=True, key=lambda x: x[1])
        
        # Get top contexts
        top_contexts = context_similarities[:3]
        
        return {
            "num_contexts": len(self.context_embeddings),
            "context_sources": [context for context, _ in top_contexts],
            "attention_scores": {context: score for context, score in top_contexts}
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "context_count": len(self.context_embeddings),
            "adaptation_count": self.adaptation_count,
            "avg_surprise_recent": self.avg_surprise_recent,
            "last_adaptation_time": self.last_adaptation_time
        }
    
    def save_state(self):
        """Save memory state to disk"""
        state_path = os.path.join(self.memory_dir, "memory_state.pkl")
        
        # Prepare memory entries for serialization
        short_term_serialized = []
        for entry in self.short_term_memory:
            entry_dict = asdict(entry)
            # Convert numpy array to list for serialization
            entry_dict["embedding"] = entry_dict["embedding"].tolist()
            short_term_serialized.append(entry_dict)
        
        long_term_serialized = []
        for entry in self.long_term_memory:
            entry_dict = asdict(entry)
            # Convert numpy array to list for serialization
            entry_dict["embedding"] = entry_dict["embedding"].tolist()
            long_term_serialized.append(entry_dict)
        
        # Convert context embeddings to lists
        context_embeddings_serialized = {
            context: embedding.tolist() 
            for context, embedding in self.context_embeddings.items()
        }
        
        # Create state object
        state = AdaptiveMemoryState(
            short_term_memory=short_term_serialized,
            long_term_memory=long_term_serialized,
            context_embeddings=context_embeddings_serialized,
            context_frequencies=self.context_frequencies,
            adaptation_count=self.adaptation_count,
            last_adaptation_time=self.last_adaptation_time,
            avg_surprise_recent=self.avg_surprise_recent,
            embedding_dim=self.embedding_dim,
            surprise_threshold=self.surprise_threshold,
            chunk_size=self.chunk_size
        )
        
        # Save to disk
        with open(state_path, 'wb') as f:
            pickle.dump(state, f)
            
        # Also save a JSON summary for inspection
        summary_path = os.path.join(self.memory_dir, "memory_summary.json")
        summary = {
            "timestamp": time.time(),
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "context_count": len(self.context_embeddings),
            "adaptation_count": self.adaptation_count,
            "contexts": list(self.context_frequencies.keys()),
            "avg_surprise": self.avg_surprise_recent
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Memory state saved to {state_path}")
    
    def load_state(self):
        """Load memory state from disk"""
        state_path = os.path.join(self.memory_dir, "memory_state.pkl")
        
        if not os.path.exists(state_path):
            print(f"Info: No memory state found at {state_path}, using fresh memory")
            return False
        
        try:
            # Load state
            with open(state_path, 'rb') as f:
                state = pickle.load(f)
            
            # Restore short-term memory
            self.short_term_memory = deque(maxlen=self.short_term_memory.maxlen)
            for entry_dict in state.short_term_memory:
                # Convert list back to numpy array
                entry_dict["embedding"] = np.array(entry_dict["embedding"])
                entry = MemoryEntry(**entry_dict)
                self.short_term_memory.append(entry)
            
            # Restore long-term memory
            self.long_term_memory = []
            for entry_dict in state.long_term_memory:
                # Convert list back to numpy array
                entry_dict["embedding"] = np.array(entry_dict["embedding"])
                entry = MemoryEntry(**entry_dict)
                self.long_term_memory.append(entry)
            
            # Restore context embeddings and frequencies
            self.context_embeddings = {}
            for context, embedding_list in state.context_embeddings.items():
                self.context_embeddings[context] = np.array(embedding_list)
            
            self.context_frequencies = state.context_frequencies
            
            # Restore other state
            self.adaptation_count = state.adaptation_count
            self.last_adaptation_time = state.last_adaptation_time
            self.avg_surprise_recent = state.avg_surprise_recent
            
            # Check compatibility
            if state.embedding_dim != self.embedding_dim:
                print(f"Warning: Loaded state has different embedding dimension "
                      f"({state.embedding_dim} vs {self.embedding_dim})")
            
            print(f"Memory state loaded from {state_path} "
                  f"({len(self.short_term_memory)} short-term, "
                  f"{len(self.long_term_memory)} long-term memories)")
            return True
            
        except Exception as e:
            print(f"Warning: Error loading memory state: {e}")
            return False
    
    def _calculate_surprise(
        self, 
        content: str, 
        context: str, 
        embedding: np.ndarray
    ) -> Tuple[float, np.ndarray]:
        """
        Calculate surprise score for new content
        
        Args:
            content: Content text
            context: Context identifier
            embedding: Content embedding
            
        Returns:
            Tuple of (surprise_score, context_embedding)
        """
        # Get context embedding if exists, or create new one
        if context in self.context_embeddings:
            context_embedding = self.context_embeddings[context]
        else:
            # If context is new, use content embedding as initial context embedding
            context_embedding = embedding.copy()
        
        # Calculate similarity to context
        context_similarity = self.embedding_engine.similarity(embedding, context_embedding)
        
        # Calculate surprise as inverse of similarity
        # Scale to make middle range more sensitive
        surprise_score = 2.0 * (1.0 - context_similarity)
        
        return surprise_score, context_embedding
    
    def _should_adapt(self) -> bool:
        """
        Determine if memory should adapt based on recent inputs
        """
        # Check if enough time has passed since last adaptation
        if time.time() - self.last_adaptation_time < 10:  # Min 10 seconds between adaptations
            return False
        
        # Check if average surprise is high enough
        if self.avg_surprise_recent < self.surprise_threshold:
            return False
        
        return True
    
    def _adapt(self):
        """
        Adapt memory weights based on recent entries
        """
        # Update word weights based on recent memories
        for memory in list(self.short_term_memory)[-self.chunk_size:]:
            # Higher surprise = more important for adaptation
            importance = min(2.0, memory.surprise_score)
            self.embedding_engine.update_weights(memory.content, importance)
        
        # Record adaptation
        self.adaptation_count += 1
        self.last_adaptation_time = time.time()
        
        print(f"+ Memory adapted weights (adaptation #{self.adaptation_count})")
    
    def _store_in_long_term(self, entry: MemoryEntry):
        """
        Store a memory entry in long-term memory
        
        Args:
            entry: Memory entry to store
        """
        # Check if content is already in long-term memory to avoid duplicates
        for existing in self.long_term_memory:
            if existing.content == entry.content:
                # Update existing entry instead of adding duplicate
                existing.access_count += 1
                existing.relevance_boost = min(0.2, 0.01 * existing.access_count)
                return
        
        # Add to long-term memory
        self.long_term_memory.append(entry)
        
        # Check capacity and remove least important if needed
        if len(self.long_term_memory) > self.long_term_capacity:
            # Calculate importance scores for each memory
            importance_scores = []
            for idx, memory in enumerate(self.long_term_memory):
                # Importance factors:
                # - access_count: more accesses = more important
                # - surprise_score: more surprising = more important
                # - recency: more recent = more important
                recency = 1.0 / (1.0 + (time.time() - memory.timestamp) / 86400)  # Days factor
                importance = (
                    0.4 * min(1.0, memory.access_count / 5.0) +  # Access count factor
                    0.3 * min(1.0, memory.surprise_score / 1.5) +  # Surprise factor
                    0.3 * recency  # Recency factor
                )
                importance_scores.append((idx, importance))
            
            # Sort by importance (ascending)
            importance_scores.sort(key=lambda x: x[1])
            
            # Remove least important
            to_remove = importance_scores[0][0]
            self.long_term_memory.pop(to_remove)