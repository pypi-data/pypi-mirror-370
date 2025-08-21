import sqlite3
import os
import json
import datetime
import time
import threading
from typing import Dict, Any, Optional, List, Union
from .memory_interface import MemoryInterface

class SQLiteMemory(MemoryInterface):
    """
    SQLite-based memory store for the agent.
    Stores user inputs, agent outputs, and other relevant data.
    """
    def __init__(self, db_path: str):
        """
        Initialize the SQLite memory store.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
    
    def _get_connection(self, timeout: float = 10.0, retries: int = 3):
        """
        Get a database connection with retry logic for concurrent access.
        
        Args:
            timeout: Connection timeout in seconds
            retries: Number of retry attempts
            
        Returns:
            sqlite3.Connection: Database connection
            
        Raises:
            sqlite3.OperationalError: If connection fails after all retries
        """
        for attempt in range(retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=timeout)
                # Enable WAL mode for better concurrent access
                conn.execute("PRAGMA journal_mode=WAL")
                # Set a reasonable busy timeout
                conn.execute("PRAGMA busy_timeout=5000")
                return conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    # Wait with exponential backoff
                    wait_time = 0.1 * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                raise
        
        # This should never be reached, but just in case
        raise sqlite3.OperationalError("Failed to get database connection after all retries")
        
    def _init_db(self):
        """Initialize the database with required tables."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Add clarification_context table
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
            CREATE TABLE IF NOT EXISTS agent_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
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
        
        # Commit and close
        conn.commit()
        conn.close()
    
    def store_input(self, user_id: str, content: str) -> None:
        """
        Store a user input in the database.
        
        Args:
            user_id: User identifier
            content: Input content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO user_inputs (user_id, content, timestamp) VALUES (?, ?, ?)",
            (user_id, content, timestamp)
        )
        
        conn.commit()
        conn.close()
    
    def store_output(self, user_id: str, content: Union[str, Dict[str, Any]]) -> None:
        """
        Store an agent output in the database.
        
        Args:
            user_id: User identifier
            content: Output content (string or dictionary)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        
        # Convert dictionary to JSON string if necessary
        if isinstance(content, dict):
            content = json.dumps(content)
        
        cursor.execute(
            "INSERT INTO agent_outputs (user_id, content, timestamp) VALUES (?, ?, ?)",
            (user_id, content, timestamp)
        )
        
        conn.commit()
        conn.close()
        
    def store_task(self, task: str, status: str = "pending") -> None:
        """
        Store a task in the database.
        
        Args:
            task: Task description
            status: Task status (default: "pending")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        created_at = datetime.datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO tasks (task, status, created_at) VALUES (?, ?, ?)",
            (task, status, created_at)
        )
        
        conn.commit()
        conn.close()
        
    def update_task_status(self, task: str, status: str = "completed") -> None:
        """
        Update the status of a task.
        
        Args:
            task: Task description
            status: New task status (default: "completed")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        completed_at = datetime.datetime.now().isoformat() if status == "completed" else None
        
        cursor.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE task = ?",
            (status, completed_at, task)
        )
        
        conn.commit()
        conn.close()
    
    def get_context(self, user_id: str, query: Optional[str] = None, limit: int = 5) -> str:
        """
        Retrieve recent interactions as context.
        In a more sophisticated system, this would use semantic search.
        
        Args:
            user_id: User identifier
            query: Optional query for context-aware retrieval
            limit: Maximum number of interactions to retrieve
            
        Returns:
            Context string
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent inputs and outputs
        cursor.execute(
            """
            SELECT 'input' as type, content, timestamp FROM user_inputs 
            WHERE user_id = ? 
            UNION ALL
            SELECT 'output' as type, content, timestamp FROM agent_outputs
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT ?
            """,
            (user_id, user_id, limit)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        # Format as context string
        context = ""
        for result_type, content, timestamp in results:
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
    
    def set_clarification_context(self, user_id: str, original_query: str) -> None:
        """
        Store the original query when awaiting clarification.
        
        Args:
            user_id: User identifier
            original_query: Original query that needs clarification
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, clear any existing clarification context for this user
        cursor.execute(
            "DELETE FROM clarification_context WHERE user_id = ?",
            (user_id,)
        )
        
        timestamp = datetime.datetime.now().isoformat()
        
        # Set the new clarification context
        cursor.execute(
            "INSERT INTO clarification_context (user_id, original_query, awaiting_clarification, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, original_query, True, timestamp)
        )
        
        conn.commit()
        conn.close()
    
    def has_clarification_flag(self, user_id: str) -> bool:
        """
        Check if we're waiting for clarification from the user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if awaiting clarification, False otherwise
        """
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
        """
        Get the original query that needed clarification.
        
        Args:
            user_id: User identifier
            
        Returns:
            Original query or None if not found
        """
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
        """
        Clear the clarification flag after receiving a response.
        
        Args:
            user_id: User identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM clarification_context WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        conn.close()