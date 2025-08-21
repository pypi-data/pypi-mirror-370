"""
Shared Knowledge Base for Multi-Agent System.

Provides centralized knowledge repository with access control, versioning,
and intelligent knowledge graph capabilities for agent collaboration.
"""
import os
import time
import threading
import uuid
import hashlib
import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Set, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import weakref

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeEntry:
    """Represents a knowledge entry in the shared knowledge base."""
    id: str
    title: str
    content: Any
    category: str
    tags: List[str]
    source_agent: str
    created_at: float
    updated_at: float
    version: int
    access_level: str  # public, restricted, private
    allowed_agents: Set[str]
    metadata: Dict[str, Any]
    relationships: Dict[str, List[str]]  # relationship_type -> [knowledge_ids]
    usage_count: int
    last_accessed: float
    
    def __post_init__(self):
        if isinstance(self.tags, str):
            self.tags = [self.tags]
        if isinstance(self.allowed_agents, list):
            self.allowed_agents = set(self.allowed_agents)
        if not self.relationships:
            self.relationships = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['allowed_agents'] = list(self.allowed_agents)
        return data


@dataclass
class KnowledgeACL:
    """Access Control List for knowledge base."""
    agent_permissions: Dict[str, Set[str]]  # agent_id -> {read, write, admin}
    category_permissions: Dict[str, Dict[str, Set[str]]]  # category -> agent_id -> permissions
    default_permissions: Set[str]
    admin_agents: Set[str]
    
    def __post_init__(self):
        if not self.agent_permissions:
            self.agent_permissions = {}
        if not self.category_permissions:
            self.category_permissions = {}
        if not self.default_permissions:
            self.default_permissions = {'read'}
        if not self.admin_agents:
            self.admin_agents = set()


@dataclass
class KnowledgeVersion:
    """Represents a version of a knowledge entry."""
    knowledge_id: str
    version: int
    content: Any
    modified_by: str
    modified_at: float
    change_summary: str
    metadata: Dict[str, Any]


@dataclass
class KnowledgeStats:
    """Statistics for the shared knowledge base."""
    total_entries: int
    categories: Dict[str, int]  # category -> count
    agents_contributing: int
    total_versions: int
    access_count_24h: int
    most_accessed: List[Tuple[str, int]]  # (knowledge_id, access_count)
    recent_additions: List[str]  # knowledge_ids
    relationship_count: int
    average_rating: float


class SharedKnowledgeBase:
    """
    Centralized knowledge repository for multi-agent collaboration.
    
    Provides secure, versioned, and searchable knowledge storage with
    relationship mapping, access control, and intelligent retrieval.
    """
    
    def __init__(self, knowledge_db_path: str = "knowledge/shared_knowledge.db"):
        """
        Initialize shared knowledge base.
        
        Args:
            knowledge_db_path: Path to SQLite database file
        """
        self.db_path = knowledge_db_path
        self.knowledge_entries: Dict[str, KnowledgeEntry] = {}
        self.knowledge_versions: Dict[str, List[KnowledgeVersion]] = defaultdict(list)
        self.acl = KnowledgeACL(
            agent_permissions={},
            category_permissions={},
            default_permissions={'read'},
            admin_agents=set()
        )
        
        # Caching and performance
        self._cache: Dict[str, Tuple[Any, float]] = {}  # knowledge_id -> (data, timestamp)
        self._cache_ttl = 300  # 5 minutes
        self._search_cache: Dict[str, Tuple[List[str], float]] = {}  # query_hash -> (results, timestamp)
        
        # Thread safety
        self._lock = threading.RLock()
        self._connection = None
        
        # Statistics and monitoring
        self.stats = KnowledgeStats(
            total_entries=0,
            categories={},
            agents_contributing=0,
            total_versions=0,
            access_count_24h=0,
            most_accessed=[],
            recent_additions=[],
            relationship_count=0,
            average_rating=0.0
        )
        
        # Create database directory
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._initialize_db()
        
        # Load existing knowledge
        self._load_knowledge_from_db()
        
        logger.info(f"SharedKnowledgeBase initialized with {len(self.knowledge_entries)} entries")
    
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
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection
    
    def _initialize_db(self):
        """Initialize database schema."""
        with self._lock:
            conn = self._get_connection()
            
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    source_agent TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    version INTEGER DEFAULT 1,
                    access_level TEXT DEFAULT 'public',
                    allowed_agents TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    relationships TEXT,  -- JSON object
                    usage_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    content_hash TEXT,
                    rating REAL DEFAULT 0.0
                );
                
                CREATE TABLE IF NOT EXISTS knowledge_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    modified_by TEXT NOT NULL,
                    modified_at REAL NOT NULL,
                    change_summary TEXT,
                    metadata TEXT,
                    FOREIGN KEY (knowledge_id) REFERENCES knowledge_entries (id)
                );
                
                CREATE TABLE IF NOT EXISTS knowledge_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_knowledge_id TEXT NOT NULL,
                    to_knowledge_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    created_by TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (from_knowledge_id) REFERENCES knowledge_entries (id),
                    FOREIGN KEY (to_knowledge_id) REFERENCES knowledge_entries (id)
                );
                
                CREATE TABLE IF NOT EXISTS knowledge_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    operation TEXT NOT NULL,  -- read, write, delete
                    timestamp REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS knowledge_acl (
                    agent_id TEXT NOT NULL,
                    category TEXT,
                    permissions TEXT NOT NULL,  -- JSON array
                    granted_by TEXT NOT NULL,
                    granted_at REAL NOT NULL,
                    PRIMARY KEY (agent_id, category)
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_entries(category);
                CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_entries(source_agent);
                CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge_entries(created_at);
                CREATE INDEX IF NOT EXISTS idx_knowledge_updated ON knowledge_entries(updated_at);
                CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_entries(tags);
                CREATE INDEX IF NOT EXISTS idx_knowledge_hash ON knowledge_entries(content_hash);
                
                CREATE INDEX IF NOT EXISTS idx_versions_knowledge ON knowledge_versions(knowledge_id);
                CREATE INDEX IF NOT EXISTS idx_versions_created ON knowledge_versions(modified_at);
                
                CREATE INDEX IF NOT EXISTS idx_relationships_from ON knowledge_relationships(from_knowledge_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_to ON knowledge_relationships(to_knowledge_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_type ON knowledge_relationships(relationship_type);
                
                CREATE INDEX IF NOT EXISTS idx_access_log_knowledge ON knowledge_access_log(knowledge_id);
                CREATE INDEX IF NOT EXISTS idx_access_log_agent ON knowledge_access_log(agent_id);
                CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON knowledge_access_log(timestamp);
            """)
            
            conn.commit()
    
    def add_knowledge(self, 
                     title: str,
                     content: Any,
                     category: str,
                     source_agent: str,
                     tags: List[str] = None,
                     access_level: str = 'public',
                     allowed_agents: Set[str] = None,
                     metadata: Dict[str, Any] = None,
                     relationships: Dict[str, List[str]] = None) -> str:
        """
        Add new knowledge to the shared knowledge base.
        
        Args:
            title: Knowledge title
            content: Knowledge content (any serializable type)
            category: Knowledge category
            source_agent: Agent ID that created this knowledge
            tags: Optional list of tags
            access_level: Access level (public, restricted, private)
            allowed_agents: Set of agent IDs allowed to access (for restricted/private)
            metadata: Optional metadata dictionary
            relationships: Optional relationships to other knowledge entries
            
        Returns:
            Knowledge entry ID
        """
        if not self._check_permission(source_agent, category, 'write'):
            raise PermissionError(f"Agent {source_agent} lacks write permission for category {category}")
        
        knowledge_id = str(uuid.uuid4())
        current_time = time.time()
        
        # Create content hash for deduplication
        content_str = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Check for duplicate content
        existing_id = self._find_by_content_hash(content_hash)
        if existing_id:
            logger.info(f"Duplicate content detected, updating existing knowledge: {existing_id}")
            success = self.update_knowledge(
                knowledge_id=existing_id, 
                title=title, 
                content=content, 
                modified_by=source_agent,
                tags=tags, 
                metadata=metadata, 
                relationships=relationships,
                change_summary="Updated duplicate content"
            )
            return existing_id if success else None
        
        # Create knowledge entry
        entry = KnowledgeEntry(
            id=knowledge_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            source_agent=source_agent,
            created_at=current_time,
            updated_at=current_time,
            version=1,
            access_level=access_level,
            allowed_agents=allowed_agents or set(),
            metadata=metadata or {},
            relationships=relationships or {},
            usage_count=0,
            last_accessed=current_time
        )
        
        with self._lock:
            # Store in memory
            self.knowledge_entries[knowledge_id] = entry
            
            # Store in database
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO knowledge_entries 
                (id, title, content, category, tags, source_agent, created_at, updated_at,
                 version, access_level, allowed_agents, metadata, relationships, 
                 usage_count, last_accessed, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                knowledge_id, title, json.dumps(content), category, json.dumps(tags),
                source_agent, current_time, current_time, 1, access_level,
                json.dumps(list(allowed_agents or [])), json.dumps(metadata or {}),
                json.dumps(relationships or {}), 0, current_time, content_hash
            ))
            
            # Create initial version
            self._create_version(knowledge_id, content, source_agent, "Initial version", metadata)
            
            # Create relationships
            if relationships:
                self._create_relationships(knowledge_id, relationships, source_agent)
            
            # Log access
            self._log_access(knowledge_id, source_agent, 'write', True)
            
            conn.commit()
            
            # Update statistics
            self._update_stats()
            
            # Clear cache
            self._clear_cache()
        
        logger.info(f"Added knowledge '{title}' (ID: {knowledge_id}) by {source_agent}")
        return knowledge_id
    
    def query_knowledge(self, 
                       query: str = None,
                       agent_id: str = None,
                       category: str = None,
                       tags: List[str] = None,
                       access_level: str = None,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query knowledge with access control.
        
        Args:
            query: Search query (searches title and content)
            agent_id: Agent making the request (for access control)
            category: Filter by category
            tags: Filter by tags (AND operation)
            access_level: Filter by access level
            limit: Maximum number of results
            
        Returns:
            List of knowledge entries (as dictionaries)
        """
        if agent_id and not self._check_permission(agent_id, category or '*', 'read'):
            return []
        
        # Generate cache key
        cache_key = hashlib.md5(
            f"{query}:{agent_id}:{category}:{tags}:{access_level}:{limit}".encode()
        ).hexdigest()
        
        # Check search cache
        if cache_key in self._search_cache:
            results, timestamp = self._search_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return [self._get_knowledge_dict(kid) for kid in results if kid in self.knowledge_entries]
        
        with self._lock:
            conn = self._get_connection()
            
            # Build query
            where_clauses = []
            params = []
            
            if query:
                where_clauses.append("(title LIKE ? OR content LIKE ?)")
                query_pattern = f"%{query}%"
                params.extend([query_pattern, query_pattern])
            
            if category:
                where_clauses.append("category = ?")
                params.append(category)
            
            if access_level:
                where_clauses.append("access_level = ?")
                params.append(access_level)
            
            if tags:
                for tag in tags:
                    where_clauses.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
            
            # Access control filter
            if agent_id:
                access_filter = """(
                    access_level = 'public' OR 
                    (access_level = 'restricted' AND (allowed_agents LIKE ? OR source_agent = ?)) OR
                    (access_level = 'private' AND source_agent = ?)
                )"""
                where_clauses.append(access_filter)
                agent_pattern = f'%"{agent_id}"%'
                params.extend([agent_pattern, agent_id, agent_id])
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            query_sql = f"""
                SELECT id, title, content, category, tags, source_agent, created_at, 
                       updated_at, version, access_level, allowed_agents, metadata,
                       relationships, usage_count, last_accessed, rating
                FROM knowledge_entries 
                WHERE {where_clause}
                ORDER BY rating DESC, updated_at DESC
                LIMIT ?
            """
            
            params.append(limit)
            
            cursor = conn.execute(query_sql, params)
            rows = cursor.fetchall()
            
            results = []
            result_ids = []
            
            for row in rows:
                knowledge_dict = self._row_to_knowledge_dict(row)
                
                # Double-check access control
                if agent_id and not self._can_access_knowledge(knowledge_dict['id'], agent_id):
                    continue
                
                results.append(knowledge_dict)
                result_ids.append(knowledge_dict['id'])
                
                # Update access statistics
                if agent_id:
                    self._update_access_stats(knowledge_dict['id'], agent_id)
            
            # Cache results
            self._search_cache[cache_key] = (result_ids, time.time())
            
            return results
    
    def get_knowledge(self, knowledge_id: str, agent_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get specific knowledge entry by ID.
        
        Args:
            knowledge_id: Knowledge entry ID
            agent_id: Agent requesting access
            
        Returns:
            Knowledge entry dictionary or None
        """
        if knowledge_id not in self.knowledge_entries:
            return None
        
        if agent_id and not self._can_access_knowledge(knowledge_id, agent_id):
            self._log_access(knowledge_id, agent_id, 'read', False)
            return None
        
        # Check cache
        cache_key = f"knowledge:{knowledge_id}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                if agent_id:
                    self._update_access_stats(knowledge_id, agent_id)
                return data
        
        with self._lock:
            knowledge_dict = self._get_knowledge_dict(knowledge_id)
            
            if knowledge_dict and agent_id:
                self._update_access_stats(knowledge_id, agent_id)
                self._log_access(knowledge_id, agent_id, 'read', True)
            
            # Cache result
            self._cache[cache_key] = (knowledge_dict, time.time())
            
            return knowledge_dict
    
    def update_knowledge(self, 
                        knowledge_id: str,
                        title: str = None,
                        content: Any = None,
                        modified_by: str = None,
                        tags: List[str] = None,
                        metadata: Dict[str, Any] = None,
                        relationships: Dict[str, List[str]] = None,
                        change_summary: str = None) -> bool:
        """
        Update existing knowledge entry.
        
        Args:
            knowledge_id: Knowledge entry ID
            title: New title (optional)
            content: New content (optional)
            modified_by: Agent making the modification
            tags: New tags (optional)
            metadata: New metadata (optional)
            relationships: New relationships (optional)
            change_summary: Summary of changes
            
        Returns:
            True if update was successful
        """
        if knowledge_id not in self.knowledge_entries:
            return False
        
        entry = self.knowledge_entries[knowledge_id]
        
        if modified_by and not self._can_modify_knowledge(knowledge_id, modified_by):
            raise PermissionError(f"Agent {modified_by} lacks permission to modify knowledge {knowledge_id}")
        
        with self._lock:
            # Update entry
            if title is not None:
                entry.title = title
            if content is not None:
                entry.content = content
            if tags is not None:
                entry.tags = tags
            if metadata is not None:
                entry.metadata.update(metadata)
            if relationships is not None:
                entry.relationships.update(relationships)
            
            entry.updated_at = time.time()
            entry.version += 1
            
            # Create new version
            if content is not None:
                self._create_version(knowledge_id, content, modified_by or 'system', 
                                   change_summary or 'Updated content', metadata)
            
            # Update database
            conn = self._get_connection()
            
            update_fields = []
            params = []
            
            if title is not None:
                update_fields.append("title = ?")
                params.append(title)
            if content is not None:
                update_fields.append("content = ?")
                params.append(json.dumps(content))
            if tags is not None:
                update_fields.append("tags = ?")
                params.append(json.dumps(tags))
            if metadata is not None:
                update_fields.append("metadata = ?")
                params.append(json.dumps(entry.metadata))
            if relationships is not None:
                update_fields.append("relationships = ?")
                params.append(json.dumps(entry.relationships))
            
            update_fields.extend(["updated_at = ?", "version = ?"])
            params.extend([entry.updated_at, entry.version])
            params.append(knowledge_id)
            
            update_sql = f"UPDATE knowledge_entries SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(update_sql, params)
            
            # Update relationships if provided
            if relationships is not None:
                self._update_relationships(knowledge_id, relationships, modified_by or 'system')
            
            # Log access
            if modified_by:
                self._log_access(knowledge_id, modified_by, 'write', True)
            
            conn.commit()
            
            # Clear cache
            self._clear_cache_for_knowledge(knowledge_id)
            
            # Update statistics
            self._update_stats()
        
        logger.info(f"Updated knowledge {knowledge_id} by {modified_by}")
        return True
    
    def delete_knowledge(self, knowledge_id: str, deleted_by: str) -> bool:
        """
        Delete knowledge entry.
        
        Args:
            knowledge_id: Knowledge entry ID
            deleted_by: Agent performing deletion
            
        Returns:
            True if deletion was successful
        """
        if knowledge_id not in self.knowledge_entries:
            return False
        
        if not self._can_modify_knowledge(knowledge_id, deleted_by):
            raise PermissionError(f"Agent {deleted_by} lacks permission to delete knowledge {knowledge_id}")
        
        with self._lock:
            # Remove from memory
            del self.knowledge_entries[knowledge_id]
            
            # Remove from database
            conn = self._get_connection()
            
            # Delete relationships
            conn.execute("DELETE FROM knowledge_relationships WHERE from_knowledge_id = ? OR to_knowledge_id = ?", 
                        (knowledge_id, knowledge_id))
            
            # Delete versions
            conn.execute("DELETE FROM knowledge_versions WHERE knowledge_id = ?", (knowledge_id,))
            
            # Delete main entry
            conn.execute("DELETE FROM knowledge_entries WHERE id = ?", (knowledge_id,))
            
            # Log access
            self._log_access(knowledge_id, deleted_by, 'delete', True)
            
            conn.commit()
            
            # Clear cache
            self._clear_cache_for_knowledge(knowledge_id)
            
            # Update statistics
            self._update_stats()
        
        logger.info(f"Deleted knowledge {knowledge_id} by {deleted_by}")
        return True
    
    def get_knowledge_graph(self, 
                          agent_id: str = None,
                          category: str = None,
                          max_depth: int = 3) -> Dict[str, Any]:
        """
        Get knowledge graph view with relationships.
        
        Args:
            agent_id: Agent requesting the graph (for access control)
            category: Filter by category
            max_depth: Maximum relationship depth to traverse
            
        Returns:
            Graph structure with nodes and edges
        """
        accessible_knowledge = self.query_knowledge(
            agent_id=agent_id,
            category=category,
            limit=1000
        )
        
        nodes = {}
        edges = []
        
        for entry in accessible_knowledge:
            knowledge_id = entry['id']
            nodes[knowledge_id] = {
                'id': knowledge_id,
                'title': entry['title'],
                'category': entry['category'],
                'tags': entry['tags'],
                'source_agent': entry['source_agent'],
                'usage_count': entry['usage_count'],
                'rating': entry.get('rating', 0.0)
            }
            
            # Add relationships as edges
            relationships = entry.get('relationships', {})
            for rel_type, related_ids in relationships.items():
                for related_id in related_ids:
                    if related_id in nodes or any(e['id'] == related_id for e in accessible_knowledge):
                        edges.append({
                            'from': knowledge_id,
                            'to': related_id,
                            'type': rel_type,
                            'strength': 1.0
                        })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'categories': list(set(node['category'] for node in nodes.values())),
                'generated_at': time.time(),
                'agent_id': agent_id
            }
        }
    
    def add_relationship(self, 
                        from_knowledge_id: str,
                        to_knowledge_id: str,
                        relationship_type: str,
                        agent_id: str,
                        strength: float = 1.0) -> bool:
        """
        Add relationship between knowledge entries.
        
        Args:
            from_knowledge_id: Source knowledge ID
            to_knowledge_id: Target knowledge ID
            relationship_type: Type of relationship
            agent_id: Agent creating the relationship
            strength: Relationship strength (0.0-1.0)
            
        Returns:
            True if relationship was created
        """
        if (from_knowledge_id not in self.knowledge_entries or 
            to_knowledge_id not in self.knowledge_entries):
            return False
        
        if not (self._can_access_knowledge(from_knowledge_id, agent_id) and
                self._can_access_knowledge(to_knowledge_id, agent_id)):
            return False
        
        with self._lock:
            conn = self._get_connection()
            
            # Check if relationship already exists
            cursor = conn.execute("""
                SELECT id FROM knowledge_relationships 
                WHERE from_knowledge_id = ? AND to_knowledge_id = ? AND relationship_type = ?
            """, (from_knowledge_id, to_knowledge_id, relationship_type))
            
            if cursor.fetchone():
                logger.info(f"Relationship already exists: {from_knowledge_id} -> {to_knowledge_id} ({relationship_type})")
                return True
            
            # Create relationship
            conn.execute("""
                INSERT INTO knowledge_relationships 
                (from_knowledge_id, to_knowledge_id, relationship_type, strength, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (from_knowledge_id, to_knowledge_id, relationship_type, strength, agent_id, time.time()))
            
            # Update in-memory relationships
            from_entry = self.knowledge_entries[from_knowledge_id]
            if relationship_type not in from_entry.relationships:
                from_entry.relationships[relationship_type] = []
            if to_knowledge_id not in from_entry.relationships[relationship_type]:
                from_entry.relationships[relationship_type].append(to_knowledge_id)
            
            conn.commit()
            
            # Clear cache
            self._clear_cache_for_knowledge(from_knowledge_id)
            self._clear_cache_for_knowledge(to_knowledge_id)
        
        logger.info(f"Added relationship: {from_knowledge_id} --{relationship_type}--> {to_knowledge_id}")
        return True
    
    def set_agent_permissions(self, 
                            agent_id: str,
                            category: str,
                            permissions: Set[str],
                            granted_by: str):
        """
        Set permissions for an agent on a category.
        
        Args:
            agent_id: Target agent ID
            category: Category (or '*' for all)
            permissions: Set of permissions ('read', 'write', 'admin')
            granted_by: Agent granting the permissions
        """
        if not self._check_permission(granted_by, category, 'admin'):
            raise PermissionError(f"Agent {granted_by} lacks admin permission for category {category}")
        
        with self._lock:
            conn = self._get_connection()
            
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_acl 
                (agent_id, category, permissions, granted_by, granted_at)
                VALUES (?, ?, ?, ?, ?)
            """, (agent_id, category, json.dumps(list(permissions)), granted_by, time.time()))
            
            # Update in-memory ACL
            if category not in self.acl.category_permissions:
                self.acl.category_permissions[category] = {}
            self.acl.category_permissions[category][agent_id] = permissions
            
            if category == '*':
                self.acl.agent_permissions[agent_id] = permissions
            
            conn.commit()
        
        logger.info(f"Set permissions for {agent_id} on {category}: {permissions}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base statistics."""
        with self._lock:
            self._update_stats()
            return asdict(self.stats)
    
    def cleanup(self):
        """Cleanup and close knowledge base."""
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None
        
        logger.info("SharedKnowledgeBase cleanup complete")
    
    # Private methods
    
    def _load_knowledge_from_db(self):
        """Load existing knowledge from database."""
        with self._lock:
            conn = self._get_connection()
            
            cursor = conn.execute("""
                SELECT id, title, content, category, tags, source_agent, created_at,
                       updated_at, version, access_level, allowed_agents, metadata,
                       relationships, usage_count, last_accessed
                FROM knowledge_entries
            """)
            
            for row in cursor.fetchall():
                entry = KnowledgeEntry(
                    id=row['id'],
                    title=row['title'],
                    content=json.loads(row['content']),
                    category=row['category'],
                    tags=json.loads(row['tags']),
                    source_agent=row['source_agent'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    version=row['version'],
                    access_level=row['access_level'],
                    allowed_agents=set(json.loads(row['allowed_agents'])),
                    metadata=json.loads(row['metadata']),
                    relationships=json.loads(row['relationships']),
                    usage_count=row['usage_count'],
                    last_accessed=row['last_accessed']
                )
                
                self.knowledge_entries[entry.id] = entry
            
            # Load ACL
            cursor = conn.execute("SELECT agent_id, category, permissions FROM knowledge_acl")
            for row in cursor.fetchall():
                agent_id = row['agent_id']
                category = row['category']
                permissions = set(json.loads(row['permissions']))
                
                if category == '*':
                    self.acl.agent_permissions[agent_id] = permissions
                else:
                    if category not in self.acl.category_permissions:
                        self.acl.category_permissions[category] = {}
                    self.acl.category_permissions[category][agent_id] = permissions
        
        logger.info(f"Loaded {len(self.knowledge_entries)} knowledge entries from database")
    
    def _check_permission(self, agent_id: str, category: str, permission: str) -> bool:
        """Check if agent has permission for category."""
        if agent_id in self.acl.admin_agents:
            return True
        
        # Check global permissions
        if agent_id in self.acl.agent_permissions:
            if permission in self.acl.agent_permissions[agent_id]:
                return True
        
        # Check category-specific permissions
        if (category in self.acl.category_permissions and 
            agent_id in self.acl.category_permissions[category]):
            if permission in self.acl.category_permissions[category][agent_id]:
                return True
        
        # Check default permissions
        return permission in self.acl.default_permissions
    
    def _can_access_knowledge(self, knowledge_id: str, agent_id: str) -> bool:
        """Check if agent can access specific knowledge."""
        if knowledge_id not in self.knowledge_entries:
            return False
        
        entry = self.knowledge_entries[knowledge_id]
        
        if entry.access_level == 'public':
            return True
        elif entry.access_level == 'private':
            return agent_id == entry.source_agent
        elif entry.access_level == 'restricted':
            return agent_id == entry.source_agent or agent_id in entry.allowed_agents
        
        return False
    
    def _can_modify_knowledge(self, knowledge_id: str, agent_id: str) -> bool:
        """Check if agent can modify specific knowledge."""
        if knowledge_id not in self.knowledge_entries:
            return False
        
        entry = self.knowledge_entries[knowledge_id]
        
        # Source agent can always modify
        if agent_id == entry.source_agent:
            return True
        
        # Check write permissions for category
        return self._check_permission(agent_id, entry.category, 'write')
    
    def _get_knowledge_dict(self, knowledge_id: str) -> Dict[str, Any]:
        """Convert knowledge entry to dictionary."""
        if knowledge_id not in self.knowledge_entries:
            return None
        
        entry = self.knowledge_entries[knowledge_id]
        return entry.to_dict()
    
    def _row_to_knowledge_dict(self, row) -> Dict[str, Any]:
        """Convert database row to knowledge dictionary."""
        return {
            'id': row['id'],
            'title': row['title'],
            'content': json.loads(row['content']),
            'category': row['category'],
            'tags': json.loads(row['tags']),
            'source_agent': row['source_agent'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'version': row['version'],
            'access_level': row['access_level'],
            'allowed_agents': set(json.loads(row['allowed_agents'])),
            'metadata': json.loads(row['metadata']),
            'relationships': json.loads(row['relationships']),
            'usage_count': row['usage_count'],
            'last_accessed': row['last_accessed'],
            'rating': row['rating'] if 'rating' in row.keys() else 0.0
        }
    
    def _create_version(self, knowledge_id: str, content: Any, modified_by: str, 
                       change_summary: str, metadata: Dict[str, Any]):
        """Create a new version of knowledge."""
        entry = self.knowledge_entries[knowledge_id]
        
        version = KnowledgeVersion(
            knowledge_id=knowledge_id,
            version=entry.version,
            content=content,
            modified_by=modified_by,
            modified_at=time.time(),
            change_summary=change_summary,
            metadata=metadata or {}
        )
        
        self.knowledge_versions[knowledge_id].append(version)
        
        # Store in database
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO knowledge_versions 
            (knowledge_id, version, content, modified_by, modified_at, change_summary, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (knowledge_id, version.version, json.dumps(content), modified_by,
              version.modified_at, change_summary, json.dumps(metadata or {})))
    
    def _create_relationships(self, knowledge_id: str, relationships: Dict[str, List[str]], agent_id: str):
        """Create relationships for knowledge entry."""
        conn = self._get_connection()
        current_time = time.time()
        
        for rel_type, related_ids in relationships.items():
            for related_id in related_ids:
                if related_id in self.knowledge_entries:
                    conn.execute("""
                        INSERT OR IGNORE INTO knowledge_relationships 
                        (from_knowledge_id, to_knowledge_id, relationship_type, strength, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (knowledge_id, related_id, rel_type, 1.0, agent_id, current_time))
    
    def _update_relationships(self, knowledge_id: str, relationships: Dict[str, List[str]], agent_id: str):
        """Update relationships for knowledge entry."""
        conn = self._get_connection()
        
        # Remove existing relationships
        conn.execute("DELETE FROM knowledge_relationships WHERE from_knowledge_id = ?", (knowledge_id,))
        
        # Add new relationships
        self._create_relationships(knowledge_id, relationships, agent_id)
    
    def _find_by_content_hash(self, content_hash: str) -> Optional[str]:
        """Find knowledge by content hash."""
        conn = self._get_connection()
        cursor = conn.execute("SELECT id FROM knowledge_entries WHERE content_hash = ?", (content_hash,))
        row = cursor.fetchone()
        return row['id'] if row else None
    
    def _update_access_stats(self, knowledge_id: str, agent_id: str):
        """Update access statistics for knowledge."""
        if knowledge_id not in self.knowledge_entries:
            return
        
        entry = self.knowledge_entries[knowledge_id]
        entry.usage_count += 1
        entry.last_accessed = time.time()
        
        # Update database
        conn = self._get_connection()
        conn.execute("""
            UPDATE knowledge_entries 
            SET usage_count = usage_count + 1, last_accessed = ?
            WHERE id = ?
        """, (entry.last_accessed, knowledge_id))
        conn.commit()
    
    def _log_access(self, knowledge_id: str, agent_id: str, operation: str, success: bool, metadata: Dict[str, Any] = None):
        """Log knowledge access."""
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO knowledge_access_log 
            (knowledge_id, agent_id, operation, timestamp, success, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (knowledge_id, agent_id, operation, time.time(), success, json.dumps(metadata or {})))
    
    def _update_stats(self):
        """Update knowledge base statistics."""
        conn = self._get_connection()
        
        # Basic counts
        cursor = conn.execute("SELECT COUNT(*) FROM knowledge_entries")
        self.stats.total_entries = cursor.fetchone()[0]
        
        # Categories
        cursor = conn.execute("SELECT category, COUNT(*) FROM knowledge_entries GROUP BY category")
        self.stats.categories = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Contributing agents
        cursor = conn.execute("SELECT COUNT(DISTINCT source_agent) FROM knowledge_entries")
        self.stats.agents_contributing = cursor.fetchone()[0]
        
        # Total versions
        cursor = conn.execute("SELECT COUNT(*) FROM knowledge_versions")
        self.stats.total_versions = cursor.fetchone()[0]
        
        # Recent access count (24h)
        yesterday = time.time() - 86400
        cursor = conn.execute("SELECT COUNT(*) FROM knowledge_access_log WHERE timestamp > ?", (yesterday,))
        self.stats.access_count_24h = cursor.fetchone()[0]
        
        # Most accessed
        cursor = conn.execute("""
            SELECT id, usage_count FROM knowledge_entries 
            ORDER BY usage_count DESC LIMIT 10
        """)
        self.stats.most_accessed = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # Recent additions
        cursor = conn.execute("""
            SELECT id FROM knowledge_entries 
            ORDER BY created_at DESC LIMIT 10
        """)
        self.stats.recent_additions = [row[0] for row in cursor.fetchall()]
        
        # Relationship count
        cursor = conn.execute("SELECT COUNT(*) FROM knowledge_relationships")
        self.stats.relationship_count = cursor.fetchone()[0]
        
        # Average rating
        cursor = conn.execute("SELECT AVG(rating) FROM knowledge_entries WHERE rating > 0")
        result = cursor.fetchone()[0]
        self.stats.average_rating = result if result else 0.0
    
    def _clear_cache(self):
        """Clear all caches."""
        self._cache.clear()
        self._search_cache.clear()
    
    def _clear_cache_for_knowledge(self, knowledge_id: str):
        """Clear cache for specific knowledge."""
        cache_key = f"knowledge:{knowledge_id}"
        self._cache.pop(cache_key, None)
        # Clear search cache (simple approach - clear all)
        self._search_cache.clear()


# Global shared knowledge base instance
_shared_knowledge: Optional[SharedKnowledgeBase] = None


def get_shared_knowledge(knowledge_db_path: str = "knowledge/shared_knowledge.db") -> SharedKnowledgeBase:
    """Get or create global shared knowledge base."""
    global _shared_knowledge
    if _shared_knowledge is None:
        _shared_knowledge = SharedKnowledgeBase(knowledge_db_path)
    return _shared_knowledge


def configure_shared_knowledge(knowledge_db_path: str = "knowledge/shared_knowledge.db") -> SharedKnowledgeBase:
    """Configure global shared knowledge base with custom settings."""
    global _shared_knowledge
    if _shared_knowledge:
        _shared_knowledge.cleanup()
    
    _shared_knowledge = SharedKnowledgeBase(knowledge_db_path)
    return _shared_knowledge