"""
Isolated Memory Management for Multi-Agent System.

Provides isolated memory spaces per agent with shared knowledge base access,
memory boundaries enforcement, and cross-agent communication policies.
"""
import os
import time
import threading
import uuid
import shutil
import logging
from typing import Dict, Any, List, Optional, Set, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from abc import ABC, abstractmethod
import sqlite3
import json
import weakref

logger = logging.getLogger(__name__)


@dataclass
class MemoryBoundary:
    """Defines memory isolation boundaries for an agent."""
    agent_id: str
    memory_path: str
    isolation_level: str  # strict, moderate, permissive
    allowed_shared_keys: Set[str]
    restricted_keys: Set[str]
    max_memory_mb: float
    cross_agent_policies: Dict[str, str]  # agent_id -> policy (deny, read, write)
    created_at: float
    
    def __post_init__(self):
        if isinstance(self.allowed_shared_keys, list):
            self.allowed_shared_keys = set(self.allowed_shared_keys)
        if isinstance(self.restricted_keys, list):
            self.restricted_keys = set(self.restricted_keys)


@dataclass
class MemoryStats:
    """Statistics for agent memory usage."""
    agent_id: str
    memory_size_mb: float
    entry_count: int
    last_accessed: float
    access_count: int
    shared_accesses: int
    isolation_violations: int
    cache_hit_rate: float
    average_query_time_ms: float


class IsolatedMemoryStore(ABC):
    """Abstract base class for isolated memory stores."""
    
    def __init__(self, agent_id: str, memory_path: str, boundary: MemoryBoundary):
        self.agent_id = agent_id
        self.memory_path = memory_path
        self.boundary = boundary
        self._access_count = 0
        self._last_accessed = time.time()
    
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store a value with optional metadata."""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """Retrieve value and metadata for a key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key-value pair."""
        pass
    
    @abstractmethod
    def list_keys(self, pattern: str = None) -> List[str]:
        """List all keys, optionally filtered by pattern."""
        pass
    
    @abstractmethod
    def get_stats(self) -> MemoryStats:
        """Get memory usage statistics."""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup and close memory store."""
        pass
    
    def _update_access_stats(self):
        """Update access statistics."""
        self._access_count += 1
        self._last_accessed = time.time()


class SQLiteIsolatedMemory(IsolatedMemoryStore):
    """SQLite-based isolated memory store."""
    
    def __init__(self, agent_id: str, memory_path: str, boundary: MemoryBoundary):
        super().__init__(agent_id, memory_path, boundary)
        self.db_path = memory_path
        self._connection = None
        self._lock = threading.RLock()
        self._query_times = []
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Create directory if needed
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._initialize_db()
        
        logger.info(f"Initialized SQLite isolated memory for agent {agent_id} at {memory_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection (thread-safe)."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=NORMAL")
        return self._connection
    
    def _initialize_db(self):
        """Initialize database schema."""
        with self._lock:
            conn = self._get_connection()
            
            # Create tables
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    expires_at REAL
                );
                
                CREATE TABLE IF NOT EXISTS memory_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    key TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metadata TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_memory_created ON agent_memory(created_at);
                CREATE INDEX IF NOT EXISTS idx_memory_updated ON agent_memory(updated_at);
                CREATE INDEX IF NOT EXISTS idx_memory_expires ON agent_memory(expires_at);
                CREATE INDEX IF NOT EXISTS idx_log_timestamp ON memory_log(timestamp);
            """)
            
            conn.commit()
    
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store a value with optional metadata."""
        if not self._validate_key_access(key, 'write'):
            logger.warning(f"Agent {self.agent_id} denied write access to key: {key}")
            return False
        
        start_time = time.time()
        
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Serialize value and metadata
                value_json = json.dumps(value)
                metadata_json = json.dumps(metadata or {})
                current_time = time.time()
                
                # Calculate expiration
                expires_at = None
                if metadata and 'ttl_seconds' in metadata:
                    expires_at = current_time + metadata['ttl_seconds']
                
                # Insert or update
                conn.execute("""
                    INSERT OR REPLACE INTO agent_memory 
                    (key, value, metadata, created_at, updated_at, expires_at)
                    VALUES (?, ?, ?, 
                        COALESCE((SELECT created_at FROM agent_memory WHERE key = ?), ?),
                        ?, ?)
                """, (key, value_json, metadata_json, key, current_time, current_time, expires_at))
                
                # Log operation
                conn.execute("""
                    INSERT INTO memory_log (operation, key, timestamp, metadata)
                    VALUES (?, ?, ?, ?)
                """, ('store', key, current_time, metadata_json))
                
                conn.commit()
                
                self._update_access_stats()
                query_time = (time.time() - start_time) * 1000
                self._query_times.append(query_time)
                
                logger.debug(f"Stored key '{key}' for agent {self.agent_id} in {query_time:.2f}ms")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store key '{key}' for agent {self.agent_id}: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """Retrieve value and metadata for a key."""
        if not self._validate_key_access(key, 'read'):
            logger.warning(f"Agent {self.agent_id} denied read access to key: {key}")
            return None
        
        start_time = time.time()
        
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Check for expiration and cleanup
                current_time = time.time()
                conn.execute("""
                    DELETE FROM agent_memory 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (current_time,))
                
                # Retrieve data
                cursor = conn.execute("""
                    SELECT value, metadata, access_count 
                    FROM agent_memory 
                    WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
                """, (key, current_time))
                
                row = cursor.fetchone()
                if row is None:
                    self._cache_misses += 1
                    return None
                
                # Update access count
                conn.execute("""
                    UPDATE agent_memory 
                    SET access_count = access_count + 1 
                    WHERE key = ?
                """, (key,))
                
                # Log access
                conn.execute("""
                    INSERT INTO memory_log (operation, key, timestamp)
                    VALUES (?, ?, ?)
                """, ('retrieve', key, current_time))
                
                conn.commit()
                
                # Deserialize data
                value = json.loads(row['value'])
                metadata = json.loads(row['metadata'])
                
                self._update_access_stats()
                self._cache_hits += 1
                
                query_time = (time.time() - start_time) * 1000
                self._query_times.append(query_time)
                
                logger.debug(f"Retrieved key '{key}' for agent {self.agent_id} in {query_time:.2f}ms")
                return value, metadata
                
        except Exception as e:
            logger.error(f"Failed to retrieve key '{key}' for agent {self.agent_id}: {e}")
            self._cache_misses += 1
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key-value pair."""
        if not self._validate_key_access(key, 'write'):
            logger.warning(f"Agent {self.agent_id} denied delete access to key: {key}")
            return False
        
        try:
            with self._lock:
                conn = self._get_connection()
                
                cursor = conn.execute("DELETE FROM agent_memory WHERE key = ?", (key,))
                deleted = cursor.rowcount > 0
                
                if deleted:
                    # Log deletion
                    conn.execute("""
                        INSERT INTO memory_log (operation, key, timestamp)
                        VALUES (?, ?, ?)
                    """, ('delete', key, time.time()))
                
                conn.commit()
                
                self._update_access_stats()
                logger.debug(f"Deleted key '{key}' for agent {self.agent_id}")
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete key '{key}' for agent {self.agent_id}: {e}")
            return False
    
    def list_keys(self, pattern: str = None) -> List[str]:
        """List all keys, optionally filtered by pattern."""
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Clean up expired entries first
                current_time = time.time()
                conn.execute("""
                    DELETE FROM agent_memory 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (current_time,))
                
                if pattern:
                    cursor = conn.execute("""
                        SELECT key FROM agent_memory 
                        WHERE key LIKE ? 
                        ORDER BY updated_at DESC
                    """, (pattern,))
                else:
                    cursor = conn.execute("""
                        SELECT key FROM agent_memory 
                        ORDER BY updated_at DESC
                    """)
                
                keys = [row['key'] for row in cursor.fetchall()]
                
                # Filter by access permissions
                accessible_keys = [
                    key for key in keys 
                    if self._validate_key_access(key, 'read')
                ]
                
                self._update_access_stats()
                return accessible_keys
                
        except Exception as e:
            logger.error(f"Failed to list keys for agent {self.agent_id}: {e}")
            return []
    
    def get_stats(self) -> MemoryStats:
        """Get memory usage statistics."""
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Get entry count
                cursor = conn.execute("SELECT COUNT(*) as count FROM agent_memory")
                entry_count = cursor.fetchone()['count']
                
                # Get database size
                memory_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
                
                # Calculate cache hit rate
                total_cache_ops = self._cache_hits + self._cache_misses
                cache_hit_rate = (self._cache_hits / total_cache_ops) if total_cache_ops > 0 else 0.0
                
                # Calculate average query time
                avg_query_time = (
                    sum(self._query_times) / len(self._query_times)
                    if self._query_times else 0.0
                )
                
                return MemoryStats(
                    agent_id=self.agent_id,
                    memory_size_mb=memory_size_mb,
                    entry_count=entry_count,
                    last_accessed=self._last_accessed,
                    access_count=self._access_count,
                    shared_accesses=0,  # Will be updated by manager
                    isolation_violations=0,  # Will be updated by manager
                    cache_hit_rate=cache_hit_rate,
                    average_query_time_ms=avg_query_time
                )
                
        except Exception as e:
            logger.error(f"Failed to get stats for agent {self.agent_id}: {e}")
            return MemoryStats(
                agent_id=self.agent_id,
                memory_size_mb=0.0,
                entry_count=0,
                last_accessed=self._last_accessed,
                access_count=self._access_count,
                shared_accesses=0,
                isolation_violations=0,
                cache_hit_rate=0.0,
                average_query_time_ms=0.0
            )
    
    def cleanup(self) -> bool:
        """Cleanup and close memory store."""
        try:
            with self._lock:
                if self._connection:
                    self._connection.close()
                    self._connection = None
                
                logger.info(f"Cleaned up isolated memory for agent {self.agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cleanup memory for agent {self.agent_id}: {e}")
            return False
    
    def _validate_key_access(self, key: str, operation: str) -> bool:
        """Validate if agent can access a key for the given operation."""
        # Check isolation level
        if self.boundary.isolation_level == "strict":
            # In strict mode, only allow access to keys in allowed_shared_keys
            if key.startswith("shared.") and key not in self.boundary.allowed_shared_keys:
                return False
            if key in self.boundary.restricted_keys:
                return False
        
        elif self.boundary.isolation_level == "moderate":
            # In moderate mode, allow most access but check restricted keys
            if key in self.boundary.restricted_keys:
                return False
        
        # "permissive" mode allows all access
        return True


class AgentMemoryManager:
    """
    Manages isolated memory spaces for multiple agents.
    
    Provides memory isolation, shared knowledge access, and cross-agent
    communication policies while maintaining performance and security.
    """
    
    def __init__(self, base_memory_dir: str = "memory/agents"):
        """
        Initialize agent memory manager.
        
        Args:
            base_memory_dir: Base directory for agent memory stores
        """
        self.base_memory_dir = Path(base_memory_dir)
        self.base_memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Core data structures
        self.agent_memories: Dict[str, IsolatedMemoryStore] = {}
        self.memory_boundaries: Dict[str, MemoryBoundary] = {}
        self.cross_agent_policies: Dict[Tuple[str, str], str] = {}  # (from_agent, to_agent) -> policy
        
        # Shared knowledge access tracking
        self.shared_knowledge_access: Dict[str, Set[str]] = {}  # key -> set of agent_ids
        self.isolation_violations: Dict[str, int] = {}  # agent_id -> violation count
        
        # Thread safety
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._shutdown = False
        
        # Start background cleanup
        self._start_cleanup_thread()
        
        logger.info(f"AgentMemoryManager initialized with base directory: {base_memory_dir}")
    
    def create_agent_memory(self, 
                          agent_id: str, 
                          memory_config: Dict[str, Any]) -> IsolatedMemoryStore:
        """
        Create isolated memory store for an agent.
        
        Args:
            agent_id: Unique agent identifier
            memory_config: Memory configuration from agent profile
            
        Returns:
            IsolatedMemoryStore instance
        """
        with self._lock:
            if agent_id in self.agent_memories:
                logger.warning(f"Memory store already exists for agent: {agent_id}")
                return self.agent_memories[agent_id]
            
            # Create memory boundary
            memory_path = str(self.base_memory_dir / f"{agent_id}.db")
            
            boundary = MemoryBoundary(
                agent_id=agent_id,
                memory_path=memory_path,
                isolation_level=memory_config.get('isolation_level', 'moderate'),
                allowed_shared_keys=set(memory_config.get('allowed_shared_keys', [])),
                restricted_keys=set(memory_config.get('restricted_keys', [])),
                max_memory_mb=memory_config.get('max_memory_mb', 100.0),
                cross_agent_policies=memory_config.get('cross_agent_policies', {}),
                created_at=time.time()
            )
            
            # Create memory store based on type
            memory_type = memory_config.get('type', 'sqlite')
            
            if memory_type == 'sqlite':
                memory_store = SQLiteIsolatedMemory(agent_id, memory_path, boundary)
            else:
                raise ValueError(f"Unsupported memory type: {memory_type}")
            
            # Register memory store
            self.agent_memories[agent_id] = memory_store
            self.memory_boundaries[agent_id] = boundary
            self.isolation_violations[agent_id] = 0
            
            logger.info(f"Created isolated memory for agent: {agent_id}")
            return memory_store
    
    def get_agent_memory(self, agent_id: str) -> Optional[IsolatedMemoryStore]:
        """
        Get agent's memory store.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            IsolatedMemoryStore or None if not found
        """
        return self.agent_memories.get(agent_id)
    
    def share_knowledge(self, 
                       from_agent: str, 
                       to_agent: str, 
                       knowledge_key: str,
                       knowledge_value: Any,
                       metadata: Dict[str, Any] = None) -> bool:
        """
        Share specific knowledge between agents.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            knowledge_key: Key for the shared knowledge
            knowledge_value: Value to share
            metadata: Optional metadata
            
        Returns:
            True if sharing was successful
        """
        # Check cross-agent policy
        policy = self.cross_agent_policies.get((from_agent, to_agent), 'deny')
        if policy == 'deny':
            logger.warning(f"Cross-agent sharing denied: {from_agent} -> {to_agent}")
            self.isolation_violations[from_agent] = self.isolation_violations.get(from_agent, 0) + 1
            return False
        
        # Get memory stores
        from_memory = self.get_agent_memory(from_agent)
        to_memory = self.get_agent_memory(to_agent)
        
        if not from_memory or not to_memory:
            logger.error(f"Memory stores not found for sharing: {from_agent} -> {to_agent}")
            return False
        
        try:
            # Create shared key
            shared_key = f"shared.{from_agent}.{knowledge_key}"
            
            # Store in target agent's memory
            share_metadata = {
                **(metadata or {}),
                'shared_from': from_agent,
                'shared_at': time.time(),
                'original_key': knowledge_key
            }
            
            success = to_memory.store(shared_key, knowledge_value, share_metadata)
            
            if success:
                # Track shared knowledge access
                if shared_key not in self.shared_knowledge_access:
                    self.shared_knowledge_access[shared_key] = set()
                self.shared_knowledge_access[shared_key].add(to_agent)
                
                logger.info(f"Shared knowledge '{knowledge_key}': {from_agent} -> {to_agent}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to share knowledge: {from_agent} -> {to_agent}: {e}")
            return False
    
    def get_memory_stats(self, agent_id: str) -> Optional[MemoryStats]:
        """
        Get memory usage statistics for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            MemoryStats or None if agent not found
        """
        memory_store = self.get_agent_memory(agent_id)
        if not memory_store:
            return None
        
        stats = memory_store.get_stats()
        
        # Add shared access and isolation violation counts
        stats.shared_accesses = sum(
            1 for agents in self.shared_knowledge_access.values()
            if agent_id in agents
        )
        stats.isolation_violations = self.isolation_violations.get(agent_id, 0)
        
        return stats
    
    def get_all_memory_stats(self) -> Dict[str, MemoryStats]:
        """Get memory statistics for all agents."""
        return {
            agent_id: self.get_memory_stats(agent_id)
            for agent_id in self.agent_memories.keys()
        }
    
    def set_cross_agent_policy(self, 
                             from_agent: str, 
                             to_agent: str, 
                             policy: str):
        """
        Set cross-agent communication policy.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            policy: Policy ('deny', 'read', 'write')
        """
        if policy not in ['deny', 'read', 'write']:
            raise ValueError(f"Invalid policy: {policy}")
        
        self.cross_agent_policies[(from_agent, to_agent)] = policy
        logger.info(f"Set cross-agent policy: {from_agent} -> {to_agent} = {policy}")
    
    def cleanup_agent_memory(self, agent_id: str) -> bool:
        """
        Cleanup and remove agent's memory store.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if cleanup was successful
        """
        with self._lock:
            memory_store = self.agent_memories.get(agent_id)
            if not memory_store:
                return False
            
            try:
                # Cleanup memory store
                memory_store.cleanup()
                
                # Remove from tracking
                del self.agent_memories[agent_id]
                del self.memory_boundaries[agent_id]
                self.isolation_violations.pop(agent_id, None)
                
                # Clean up shared knowledge references
                for key, agents in list(self.shared_knowledge_access.items()):
                    agents.discard(agent_id)
                    if not agents:
                        del self.shared_knowledge_access[key]
                
                # Remove database file
                memory_path = memory_store.memory_path
                if os.path.exists(memory_path):
                    os.remove(memory_path)
                
                logger.info(f"Cleaned up memory for agent: {agent_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cleanup memory for agent {agent_id}: {e}")
                return False
    
    def get_isolation_report(self) -> Dict[str, Any]:
        """Get comprehensive isolation and security report."""
        with self._lock:
            total_agents = len(self.agent_memories)
            total_violations = sum(self.isolation_violations.values())
            
            # Calculate memory distribution
            memory_stats = self.get_all_memory_stats()
            total_memory = sum(stats.memory_size_mb for stats in memory_stats.values() if stats)
            
            # Cross-agent policies summary
            policy_summary = {}
            for (from_agent, to_agent), policy in self.cross_agent_policies.items():
                if policy not in policy_summary:
                    policy_summary[policy] = 0
                policy_summary[policy] += 1
            
            return {
                'total_agents': total_agents,
                'total_memory_mb': total_memory,
                'total_isolation_violations': total_violations,
                'shared_knowledge_keys': len(self.shared_knowledge_access),
                'cross_agent_policies': policy_summary,
                'agent_memory_stats': {
                    agent_id: asdict(stats) if stats else None
                    for agent_id, stats in memory_stats.items()
                },
                'isolation_violations_by_agent': dict(self.isolation_violations),
                'timestamp': time.time()
            }
    
    def shutdown(self):
        """Shutdown memory manager and cleanup all resources."""
        logger.info("Shutting down AgentMemoryManager...")
        
        with self._lock:
            self._shutdown = True
            
            # Stop cleanup thread
            if self._cleanup_thread and self._cleanup_thread.is_alive():
                self._cleanup_thread.join(timeout=5.0)
            
            # Cleanup all agent memories
            agent_ids = list(self.agent_memories.keys())
            for agent_id in agent_ids:
                self.cleanup_agent_memory(agent_id)
        
        logger.info("AgentMemoryManager shutdown complete")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while not self._shutdown:
                try:
                    time.sleep(300)  # Check every 5 minutes
                    if not self._shutdown:
                        self._cleanup_expired_shared_knowledge()
                except Exception as e:
                    logger.error(f"Error in memory cleanup thread: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.debug("Memory cleanup thread started")
    
    def _cleanup_expired_shared_knowledge(self):
        """Cleanup expired shared knowledge entries."""
        current_time = time.time()
        cleanup_count = 0
        
        for memory_store in self.agent_memories.values():
            try:
                # This will trigger cleanup of expired entries in each store
                memory_store.list_keys()
                cleanup_count += 1
            except Exception as e:
                logger.error(f"Error cleaning up memory store: {e}")
        
        if cleanup_count > 0:
            logger.debug(f"Cleaned up expired entries in {cleanup_count} memory stores")


# Global memory manager instance
_memory_manager: Optional[AgentMemoryManager] = None


def get_memory_manager(base_memory_dir: str = "memory/agents") -> AgentMemoryManager:
    """Get or create global agent memory manager."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = AgentMemoryManager(base_memory_dir)
    return _memory_manager


def configure_memory_manager(base_memory_dir: str = "memory/agents") -> AgentMemoryManager:
    """Configure global agent memory manager with custom settings."""
    global _memory_manager
    if _memory_manager:
        _memory_manager.shutdown()
    
    _memory_manager = AgentMemoryManager(base_memory_dir)
    return _memory_manager