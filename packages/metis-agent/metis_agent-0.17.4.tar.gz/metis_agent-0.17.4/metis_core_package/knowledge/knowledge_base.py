"""
Core Knowledge Base Implementation

Provides the main KnowledgeBase class that handles storage, retrieval, and
management of knowledge entries with SQLite backend and optional external
provider integration.
"""

import os
import sqlite3
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from difflib import SequenceMatcher

from .knowledge_entry import KnowledgeEntry, KnowledgeQueryResult
from .knowledge_config import KnowledgeConfig


class KnowledgeBase:
    """
    Core knowledge base implementation with SQLite storage
    """
    
    def __init__(self, config: KnowledgeConfig):
        self.config = config
        self.db_path = config.database_path
        
        # Initialize database
        self._init_database()
        
        # External provider (if configured)
        self.external_provider = None
        if config.external_provider:
            self._init_external_provider()
        
        # Initialize graph components (lazy loading)
        self.graph = None
        self.graph_retriever = None
        self.relationship_analyzer = None
        
        # Initialize graph if enabled
        if getattr(config, 'enable_graph', True):
            self._init_graph_components()
    
    def _init_database(self):
        """Initialize SQLite database with knowledge base schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Knowledge entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,  -- JSON array of tags
                    source TEXT NOT NULL,  -- file, ai_generated, external, user_input
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1,
                    embedding BLOB,  -- Vector embedding for similarity search
                    metadata TEXT,  -- JSON metadata
                    centrality_score REAL DEFAULT 0.0,  -- Graph centrality score
                    connection_count INTEGER DEFAULT 0  -- Number of graph connections
                )
            ''')
            
            # Knowledge categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    parent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES knowledge_categories(id)
                )
            ''')
            
            # Knowledge tags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT,
                    description TEXT
                )
            ''')
            
            # Knowledge versions table (for version history)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    change_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,  -- user or ai_agent
                    FOREIGN KEY (knowledge_id) REFERENCES knowledge_entries(id)
                )
            ''')
            
            # Knowledge relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,  -- related, depends_on, contradicts, etc.
                    strength REAL DEFAULT 1.0,
                    usage_count INTEGER DEFAULT 0,  -- How often this relationship is used
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When relationship was last accessed
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES knowledge_entries(id),
                    FOREIGN KEY (target_id) REFERENCES knowledge_entries(id)
                )
            ''')
            
            # Graph cache table for performance optimization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS graph_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_entries(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_entries(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_updated ON knowledge_entries(updated_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_entries(tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_centrality ON knowledge_entries(centrality_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON knowledge_relationships(source_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON knowledge_relationships(target_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_type ON knowledge_relationships(relationship_type)')
            
            conn.commit()
    
    def _init_external_provider(self):
        """Initialize external provider if configured"""
        # TODO: Implement external provider initialization
        # This will be implemented in Phase 3
        pass
    
    def _init_graph_components(self):
        """Initialize graph components"""
        try:
            from .graph import KnowledgeGraph, GraphKnowledgeRetriever, RelationshipAnalyzer
            
            # Initialize graph
            self.graph = KnowledgeGraph(self)
            
            # Initialize retriever
            self.graph_retriever = GraphKnowledgeRetriever(self.graph)
            
            # Initialize relationship analyzer
            self.relationship_analyzer = RelationshipAnalyzer(self)
            
            print("Graph components initialized successfully")
            
        except ImportError as e:
            print(f"Warning: Graph components not available: {e}")
            print("Install required dependencies: pip install networkx scikit-learn")
        except Exception as e:
            print(f"Warning: Error initializing graph components: {e}")
            # Continue without graph functionality
    
    def store(self, entry: KnowledgeEntry) -> bool:
        """Store a knowledge entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert tags to JSON string
                import json
                tags_json = json.dumps(entry.tags)
                metadata_json = json.dumps(entry.metadata)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_entries 
                    (id, title, content, category, tags, source, created_at, updated_at, version, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.id,
                    entry.title,
                    entry.content,
                    entry.category,
                    tags_json,
                    entry.source,
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat(),
                    entry.version,
                    metadata_json
                ))
                
                conn.commit()
                
                # Add to graph if available
                if self.graph:
                    try:
                        self.graph.add_entry_to_graph(entry)
                    except Exception as e:
                        print(f"Warning: Error adding entry to graph: {e}")
                
                return True
                
        except Exception as e:
            print(f"Error storing knowledge entry: {e}")
            return False
    
    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get a knowledge entry by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM knowledge_entries WHERE id = ?', (entry_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_entry(row)
                return None
                
        except Exception as e:
            print(f"Error retrieving knowledge entry: {e}")
            return None
    
    def search(self, query: str, category: Optional[str] = None, 
               tags: Optional[List[str]] = None, max_results: int = 10,
               similarity_threshold: float = None, use_graph: bool = True,
               include_related: bool = False, max_depth: int = 2) -> KnowledgeQueryResult:
        """Search knowledge entries with optional graph enhancement"""
        start_time = time.time()
        
        if similarity_threshold is None:
            similarity_threshold = self.config.similarity_threshold
        
        # Use graph-enhanced search if available and requested
        if use_graph and self.graph_retriever and (include_related or max_depth > 1):
            try:
                return self.graph_retriever.search_with_context(
                    query=query,
                    include_related=include_related,
                    max_depth=max_depth,
                    category=category,
                    tags=tags,
                    max_results=max_results,
                    similarity_threshold=similarity_threshold
                )
            except Exception as e:
                print(f"Warning: Graph search failed, falling back to traditional search: {e}")
        
        # Traditional search implementation
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query conditions
                conditions = []
                params = []
                
                if category:
                    conditions.append('category = ?')
                    params.append(category)
                
                if tags:
                    # Search for entries that contain any of the specified tags
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append('tags LIKE ?')
                        params.append(f'%"{tag}"%')
                    if tag_conditions:
                        conditions.append(f"({' OR '.join(tag_conditions)})")
                
                # Build SQL query
                where_clause = ' AND '.join(conditions) if conditions else '1=1'
                sql = f'''
                    SELECT * FROM knowledge_entries 
                    WHERE {where_clause}
                    ORDER BY updated_at DESC
                    LIMIT ?
                '''
                params.append(max_results * 3)  # Get more results for similarity filtering
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                # Convert to entries and calculate relevance
                entries_with_scores = []
                for row in rows:
                    entry = self._row_to_entry(row)
                    if entry:
                        # Calculate relevance score
                        relevance = self._calculate_relevance(query, entry)
                        if relevance >= similarity_threshold:
                            entries_with_scores.append((entry, relevance))
                
                # Sort by relevance and limit results
                entries_with_scores.sort(key=lambda x: x[1], reverse=True)
                entries_with_scores = entries_with_scores[:max_results]
                
                entries = [entry for entry, _ in entries_with_scores]
                scores = [score for _, score in entries_with_scores]
                
                execution_time = time.time() - start_time
                
                return KnowledgeQueryResult(
                    entries=entries,
                    total_count=len(entries),
                    query=query,
                    filters={'category': category, 'tags': tags},
                    execution_time=execution_time,
                    relevance_scores=scores
                )
                
        except Exception as e:
            print(f"Error searching knowledge entries: {e}")
            return KnowledgeQueryResult(
                entries=[],
                total_count=0,
                query=query,
                filters={'category': category, 'tags': tags},
                execution_time=time.time() - start_time,
                relevance_scores=[]
            )
    
    def list_entries(self, category: Optional[str] = None, 
                     tags: Optional[List[str]] = None,
                     limit: int = 50) -> List[KnowledgeEntry]:
        """List knowledge entries with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query conditions
                conditions = []
                params = []
                
                if category:
                    conditions.append('category = ?')
                    params.append(category)
                
                if tags:
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append('tags LIKE ?')
                        params.append(f'%"{tag}"%')
                    if tag_conditions:
                        conditions.append(f"({' OR '.join(tag_conditions)})")
                
                where_clause = ' AND '.join(conditions) if conditions else '1=1'
                sql = f'''
                    SELECT * FROM knowledge_entries 
                    WHERE {where_clause}
                    ORDER BY updated_at DESC
                    LIMIT ?
                '''
                params.append(limit)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [self._row_to_entry(row) for row in rows if self._row_to_entry(row)]
                
        except Exception as e:
            print(f"Error listing knowledge entries: {e}")
            return []
    
    def delete(self, entry_id: str) -> bool:
        """Delete a knowledge entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM knowledge_entries WHERE id = ?', (entry_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting knowledge entry: {e}")
            return False
    
    def update(self, entry: KnowledgeEntry) -> bool:
        """Update an existing knowledge entry"""
        entry.updated_at = datetime.now()
        return self.store(entry)
    
    def get_categories(self) -> List[str]:
        """Get all categories in use"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT category FROM knowledge_entries ORDER BY category')
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_tags(self) -> List[str]:
        """Get all tags in use"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT tags FROM knowledge_entries WHERE tags IS NOT NULL')
                
                # Extract individual tags from JSON arrays
                import json
                all_tags = set()
                for row in cursor.fetchall():
                    try:
                        tags = json.loads(row[0])
                        all_tags.update(tags)
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                return sorted(list(all_tags))
                
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total entries
                cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
                total_entries = cursor.fetchone()[0]
                
                # Entries by category
                cursor.execute('SELECT category, COUNT(*) FROM knowledge_entries GROUP BY category')
                categories = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Entries by source
                cursor.execute('SELECT source, COUNT(*) FROM knowledge_entries GROUP BY source')
                sources = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Recent activity (last 7 days)
                cursor.execute('''
                    SELECT COUNT(*) FROM knowledge_entries 
                    WHERE updated_at >= datetime('now', '-7 days')
                ''')
                recent_updates = cursor.fetchone()[0]
                
                return {
                    'total_entries': total_entries,
                    'categories': categories,
                    'sources': sources,
                    'recent_updates': recent_updates,
                    'database_path': self.db_path,
                    'external_provider': self.config.external_provider
                }
                
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def import_from_file(self, file_path: str, category: str = None, 
                         tags: List[str] = None) -> Optional[KnowledgeEntry]:
        """Import knowledge from a file"""
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate entry ID
            entry_id = f"kb_{uuid.uuid4().hex[:8]}"
            
            # Determine category from file path if not provided
            if not category:
                # Try to extract category from file path
                path_parts = os.path.normpath(file_path).split(os.sep)
                if len(path_parts) > 1:
                    category = path_parts[-2]  # Parent directory name
                else:
                    category = "general"
            
            # Create entry from file content
            if file_path.endswith('.md'):
                entry = KnowledgeEntry.from_markdown(content, entry_id)
            else:
                # Plain text file
                filename = os.path.basename(file_path)
                title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
                
                entry = KnowledgeEntry(
                    id=entry_id,
                    title=title,
                    content=content,
                    category=category,
                    tags=tags or [],
                    source="file"
                )
            
            # Override category and tags if provided
            if category:
                entry.category = category
            if tags:
                entry.tags = tags
            
            # Store the entry
            if self.store(entry):
                return entry
            else:
                return None
                
        except Exception as e:
            print(f"Error importing from file {file_path}: {e}")
            return None
    
    def export_to_file(self, entry_id: str, file_path: str, format: str = 'md') -> bool:
        """Export knowledge entry to file"""
        try:
            entry = self.get(entry_id)
            if not entry:
                print(f"Entry not found: {entry_id}")
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Export in specified format
            if format == 'md':
                content = entry.to_markdown()
            elif format == 'json':
                content = entry.to_json()
            elif format == 'yaml':
                content = entry.to_yaml()
            else:
                print(f"Unsupported format: {format}")
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to file {file_path}: {e}")
            return False
    
    def _row_to_entry(self, row) -> Optional[KnowledgeEntry]:
        """Convert database row to KnowledgeEntry"""
        try:
            import json
            
            # Parse row data
            (id, title, content, category, tags_json, source, 
             created_at, updated_at, version, embedding, metadata_json, 
             centrality_score, connection_count) = row
            
            # Parse JSON fields
            tags = json.loads(tags_json) if tags_json else []
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            # Parse datetime strings
            created_dt = datetime.fromisoformat(created_at)
            updated_dt = datetime.fromisoformat(updated_at)
            
            return KnowledgeEntry(
                id=id,
                title=title,
                content=content,
                category=category,
                tags=tags,
                source=source,
                created_at=created_dt,
                updated_at=updated_dt,
                version=version,
                embedding=None,  # TODO: Handle embedding deserialization
                metadata=metadata
            )
            
        except Exception as e:
            print(f"Error converting row to entry: {e}")
            return None
    
    def _calculate_relevance(self, query: str, entry: KnowledgeEntry) -> float:
        """Calculate relevance score between query and entry"""
        query_lower = query.lower()
        
        # Title similarity (weighted higher)
        title_similarity = SequenceMatcher(None, query_lower, entry.title.lower()).ratio()
        
        # Content similarity
        content_similarity = SequenceMatcher(None, query_lower, entry.content.lower()).ratio()
        
        # Tag matching
        tag_similarity = 0.0
        if entry.tags:
            for tag in entry.tags:
                if query_lower in tag.lower() or tag.lower() in query_lower:
                    tag_similarity = max(tag_similarity, 0.8)
        
        # Category matching
        category_similarity = 0.0
        if query_lower in entry.category.lower() or entry.category.lower() in query_lower:
            category_similarity = 0.6
        
        # Weighted combination
        relevance = (
            title_similarity * 0.4 +
            content_similarity * 0.3 +
            tag_similarity * 0.2 +
            category_similarity * 0.1
        )
        
        return relevance
