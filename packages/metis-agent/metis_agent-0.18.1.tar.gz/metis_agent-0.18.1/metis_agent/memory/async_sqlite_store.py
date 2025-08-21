"""
Async SQLite Memory Store with Connection Pooling for Metis Agent.

This module provides high-performance async SQLite operations with:
- Connection pooling to reduce overhead
- Async/await support for non-blocking database operations
- Transaction batching for bulk operations
- Optimized indexing and query performance
- Backward compatibility with existing SQLiteMemory interface
"""

import sqlite3
import aiosqlite
import asyncio
import os
import json
import datetime
from typing import Dict, Any, Optional, List, Union, AsyncContextManager
from contextlib import asynccontextmanager
from .memory_interface import MemoryInterface


class AsyncSQLiteMemory(MemoryInterface):
    """
    High-performance async SQLite memory store with connection pooling.
    
    Features:
    - Async/await database operations
    - Connection pooling (configurable pool size)
    - Optimized indexing for better query performance
    - Transaction batching for bulk operations
    - Backward compatibility with sync interface
    """
    
    def __init__(self, db_path: str, pool_size: int = 5, enable_wal: bool = True):
        """
        Initialize the async SQLite memory store.
        
        Args:
            db_path: Path to the SQLite database file
            pool_size: Maximum number of concurrent database connections
            enable_wal: Enable Write-Ahead Logging for better performance
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.enable_wal = enable_wal
        self._pool = asyncio.Queue(maxsize=pool_size)
        self._pool_initialized = False
        self._lock = asyncio.Lock()
        
        # Initialize database synchronously first for compatibility
        self._init_db_sync()
    
    def _init_db_sync(self):
        """Initialize the database synchronously (for compatibility)."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrent performance
        if self.enable_wal:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=memory")
        
        # Create tables compatible with existing schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Add enhanced columns safely
        try:
            cursor.execute('ALTER TABLE user_inputs ADD COLUMN metadata TEXT')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE user_inputs ADD COLUMN content_hash TEXT')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE agent_outputs ADD COLUMN processing_time REAL')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE agent_outputs ADD COLUMN metadata TEXT')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE agent_outputs ADD COLUMN content_hash TEXT')
        except sqlite3.OperationalError:
            pass
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clarification_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                original_query TEXT NOT NULL,
                awaiting_clarification BOOLEAN NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        
        # Add enhanced task columns safely
        try:
            cursor.execute('ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE tasks ADD COLUMN metadata TEXT')
        except sqlite3.OperationalError:
            pass
        
        # Create performance indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_inputs_user_timestamp 
            ON user_inputs(user_id, timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_outputs_user_timestamp 
            ON agent_outputs(user_id, timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_clarification_user_status 
            ON clarification_context(user_id, awaiting_clarification)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tasks_status_created 
            ON tasks(status, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_inputs_content_hash 
            ON user_inputs(content_hash)
        ''')
        
        # Commit and close
        conn.commit()
        conn.close()
    
    async def _init_connection_pool(self):
        """Initialize the async connection pool."""
        if self._pool_initialized:
            return
            
        async with self._lock:
            if self._pool_initialized:
                return
                
            # Create pool of database connections
            for _ in range(self.pool_size):
                conn = await aiosqlite.connect(self.db_path)
                
                # Configure connection for performance
                if self.enable_wal:
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=10000")
                    await conn.execute("PRAGMA temp_store=memory")
                
                await self._pool.put(conn)
            
            self._pool_initialized = True
    
    @asynccontextmanager
    async def _get_connection(self) -> AsyncContextManager[aiosqlite.Connection]:
        """Get a connection from the pool."""
        if not self._pool_initialized:
            await self._init_connection_pool()
        
        # Get connection from pool
        conn = await self._pool.get()
        try:
            yield conn
        finally:
            # Return connection to pool
            await self._pool.put(conn)
    
    async def store_input_async(self, user_id: str, content: str, metadata: Dict[str, Any] = None) -> int:
        """
        Store a user input asynchronously.
        
        Args:
            user_id: User identifier
            content: Input content
            metadata: Optional metadata dictionary
            
        Returns:
            The ID of the inserted record
        """
        async with self._get_connection() as conn:
            timestamp = datetime.datetime.now().isoformat()
            content_hash = str(hash(content))
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor = await conn.execute(
                """INSERT INTO user_inputs 
                   (user_id, content, timestamp, content_hash, metadata) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, content, timestamp, content_hash, metadata_json)
            )
            
            await conn.commit()
            return cursor.lastrowid
    
    async def store_output_async(self, user_id: str, content: Union[str, Dict[str, Any]], 
                                processing_time: float = None, metadata: Dict[str, Any] = None) -> int:
        """
        Store an agent output asynchronously.
        
        Args:
            user_id: User identifier
            content: Output content (string or dictionary)
            processing_time: Time taken to generate the response
            metadata: Optional metadata dictionary
            
        Returns:
            The ID of the inserted record
        """
        async with self._get_connection() as conn:
            timestamp = datetime.datetime.now().isoformat()
            
            # Convert dictionary to JSON string if necessary
            if isinstance(content, dict):
                content_str = json.dumps(content)
            else:
                content_str = str(content)
            
            content_hash = str(hash(content_str))
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor = await conn.execute(
                """INSERT INTO agent_outputs 
                   (user_id, content, timestamp, content_hash, metadata, processing_time) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, content_str, timestamp, content_hash, metadata_json, processing_time)
            )
            
            await conn.commit()
            return cursor.lastrowid
    
    async def get_context_async(self, user_id: str, query: Optional[str] = None, 
                               limit: int = 5, include_metadata: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Retrieve recent interactions as context asynchronously.
        
        Args:
            user_id: User identifier
            query: Optional query for context-aware retrieval
            limit: Maximum number of interactions to retrieve
            include_metadata: Whether to include metadata in response
            
        Returns:
            Context string or detailed dictionary if include_metadata=True
        """
        async with self._get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT 'input' as type, content, timestamp, metadata, content_hash FROM user_inputs 
                WHERE user_id = ? 
                UNION ALL
                SELECT 'output' as type, content, timestamp, metadata, NULL as content_hash FROM agent_outputs
                WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
                """,
                (user_id, user_id, limit)
            )
            
            results = await cursor.fetchall()
            
            if include_metadata:
                # Return detailed structure
                interactions = []
                for result_type, content, timestamp, metadata_json, content_hash in results:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    interactions.append({
                        "type": result_type,
                        "content": content,
                        "timestamp": timestamp,
                        "metadata": metadata,
                        "content_hash": content_hash
                    })
                
                return {
                    "user_id": user_id,
                    "interactions": interactions,
                    "total_count": len(interactions)
                }
            
            # Return formatted context string (backward compatibility)
            context = ""
            for result_type, content, timestamp, metadata_json, content_hash in results:
                time_str = datetime.datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
                if result_type == "input":
                    context += f"User ({time_str}): {content}\n"
                else:
                    # Try to parse JSON content
                    try:
                        content_obj = json.loads(content)
                        if isinstance(content_obj, dict) and "data" in content_obj:
                            if "answer" in content_obj["data"]:
                                content = content_obj["data"]["answer"]
                            elif "summary" in content_obj["data"]:
                                content = content_obj["data"]["summary"]
                    except:
                        pass
                    
                    context += f"Agent ({time_str}): {content}\n"
            
            return context
    
    async def batch_store_async(self, operations: List[Dict[str, Any]]) -> List[int]:
        """
        Perform multiple store operations in a single transaction.
        
        Args:
            operations: List of operation dictionaries with keys:
                       'type': 'input' or 'output'
                       'user_id': str
                       'content': str
                       'metadata': Optional[Dict]
                       'processing_time': Optional[float] (for outputs only)
        
        Returns:
            List of inserted record IDs
        """
        async with self._get_connection() as conn:
            await conn.execute("BEGIN TRANSACTION")
            
            try:
                inserted_ids = []
                
                for op in operations:
                    timestamp = datetime.datetime.now().isoformat()
                    content = op['content']
                    content_hash = str(hash(content))
                    metadata_json = json.dumps(op.get('metadata')) if op.get('metadata') else None
                    
                    if op['type'] == 'input':
                        cursor = await conn.execute(
                            """INSERT INTO user_inputs 
                               (user_id, content, timestamp, content_hash, metadata) 
                               VALUES (?, ?, ?, ?, ?)""",
                            (op['user_id'], content, timestamp, content_hash, metadata_json)
                        )
                    elif op['type'] == 'output':
                        processing_time = op.get('processing_time')
                        cursor = await conn.execute(
                            """INSERT INTO agent_outputs 
                               (user_id, content, timestamp, content_hash, metadata, processing_time) 
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (op['user_id'], content, timestamp, content_hash, metadata_json, processing_time)
                        )
                    
                    inserted_ids.append(cursor.lastrowid)
                
                await conn.commit()
                return inserted_ids
                
            except Exception as e:
                await conn.rollback()
                raise e
    
    # Sync compatibility methods (delegate to async versions)
    def store_input(self, user_id: str, content: str) -> None:
        """Sync wrapper for store_input_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context, create a task
                asyncio.create_task(self.store_input_async(user_id, content))
            else:
                loop.run_until_complete(self.store_input_async(user_id, content))
        except RuntimeError:
            # No event loop, run in new loop
            asyncio.run(self.store_input_async(user_id, content))
    
    def store_output(self, user_id: str, content: Union[str, Dict[str, Any]]) -> None:
        """Sync wrapper for store_output_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.store_output_async(user_id, content))
            else:
                loop.run_until_complete(self.store_output_async(user_id, content))
        except RuntimeError:
            asyncio.run(self.store_output_async(user_id, content))
    
    def get_context(self, user_id: str, query: Optional[str] = None, limit: int = 5) -> str:
        """Sync wrapper for get_context_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a future that will be resolved
                future = asyncio.ensure_future(self.get_context_async(user_id, query, limit))
                # For now, return a placeholder - in practice this should be handled differently
                return f"[Async context retrieval in progress for user {user_id}]"
            else:
                return loop.run_until_complete(self.get_context_async(user_id, query, limit))
        except RuntimeError:
            return asyncio.run(self.get_context_async(user_id, query, limit))
    
    # Task management (keeping existing interface)
    async def store_task_async(self, task: str, status: str = "pending", 
                              priority: int = 1, metadata: Dict[str, Any] = None) -> int:
        """Store a task asynchronously with priority and metadata."""
        async with self._get_connection() as conn:
            created_at = datetime.datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor = await conn.execute(
                """INSERT INTO tasks (task, status, created_at, priority, metadata) 
                   VALUES (?, ?, ?, ?, ?)""",
                (task, status, created_at, priority, metadata_json)
            )
            
            await conn.commit()
            return cursor.lastrowid
    
    def store_task(self, task: str, status: str = "pending") -> None:
        """Sync wrapper for store_task_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.store_task_async(task, status))
            else:
                loop.run_until_complete(self.store_task_async(task, status))
        except RuntimeError:
            asyncio.run(self.store_task_async(task, status))
    
    # Clarification context methods (keeping existing interface)
    def set_clarification_context(self, user_id: str, original_query: str) -> None:
        """Store the original query when awaiting clarification."""
        # Use sync implementation for simplicity (these are not performance critical)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clarification_context WHERE user_id = ?", (user_id,))
        
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO clarification_context (user_id, original_query, awaiting_clarification, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, original_query, True, timestamp)
        )
        
        conn.commit()
        conn.close()
    
    def has_clarification_flag(self, user_id: str) -> bool:
        """Check if we're waiting for clarification from the user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM clarification_context WHERE user_id = ? AND awaiting_clarification = 1",
            (user_id,)
        )
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    def get_clarification_context(self, user_id: str) -> Optional[str]:
        """Get the original query that needed clarification."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT original_query FROM clarification_context WHERE user_id = ? AND awaiting_clarification = 1",
            (user_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def clear_clarification_flag(self, user_id: str) -> None:
        """Clear the clarification flag after receiving a response."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clarification_context WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def update_task_status(self, task: str, status: str = "completed") -> None:
        """Update the status of a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        completed_at = datetime.datetime.now().isoformat() if status == "completed" else None
        
        cursor.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE task = ?",
            (status, completed_at, task)
        )
        
        conn.commit()
        conn.close()
    
    async def close(self):
        """Close all connections in the pool."""
        if not self._pool_initialized:
            return
            
        # Close all connections in pool
        while not self._pool.empty():
            conn = await self._pool.get()
            await conn.close()