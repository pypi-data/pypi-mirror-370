"""
Enhanced Memory Manager for Metis Agent

This module provides intelligent memory management with:
- Token-aware context limits
- Intelligent summarization
- Session cleanup
- Cost optimization
"""

import os
import json
import time
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MemoryConfig:
    """Configuration for memory management"""
    max_context_tokens: int = 2000  # Max tokens for context
    max_interactions_per_session: int = 20  # Max interactions to keep
    summarization_threshold: int = 10  # When to start summarizing
    session_timeout_hours: int = 24  # Auto-cleanup sessions older than this
    enable_cost_tracking: bool = True
    enable_summarization: bool = True

@dataclass
class ContextStats:
    """Statistics about context usage"""
    total_interactions: int
    estimated_tokens: int
    summarized_interactions: int
    raw_interactions: int
    session_age_hours: float

class EnhancedMemoryManager:
    """
    Enhanced memory manager with token awareness and intelligent summarization
    """
    
    def __init__(self, db_path: str, config: Optional[MemoryConfig] = None):
        """
        Initialize enhanced memory manager
        
        Args:
            db_path: Path to SQLite database
            config: Memory configuration
        """
        self.db_path = db_path
        self.config = config or MemoryConfig()
        self._init_db()
        
    def _init_db(self):
        """Initialize database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced tables with token tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                agent_output TEXT NOT NULL,
                estimated_tokens INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                is_summarized BOOLEAN DEFAULT FALSE,
                summary_of_interactions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                summary_text TEXT NOT NULL,
                interactions_summarized INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                total_tokens_used INTEGER DEFAULT 0,
                api_calls_made INTEGER DEFAULT 0,
                cost_estimate REAL DEFAULT 0.0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_timestamp ON conversations(session_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_summaries ON session_summaries(session_id)')
        
        conn.commit()
        conn.close()
    
    def store_interaction(self, session_id: str, user_input: str, agent_output: str) -> Dict[str, Any]:
        """
        Store interaction with token estimation and intelligent management
        
        Args:
            session_id: Session identifier
            user_input: User's input
            agent_output: Agent's response
            
        Returns:
            Storage info with token estimates and recommendations
        """
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = (len(user_input) + len(agent_output)) // 4
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store the interaction
        cursor.execute('''
            INSERT INTO conversations 
            (session_id, user_input, agent_output, estimated_tokens, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_input, agent_output, estimated_tokens, datetime.now().isoformat()))
        
        # Update session stats
        self._update_session_stats(cursor, session_id, estimated_tokens)
        
        conn.commit()
        
        # Check if summarization is needed
        interaction_count = self._get_interaction_count(cursor, session_id)
        needs_summarization = (
            self.config.enable_summarization and 
            interaction_count >= self.config.summarization_threshold and
            interaction_count % 5 == 0  # Summarize every 5 interactions after threshold
        )
        
        conn.close()
        
        result = {
            "stored": True,
            "estimated_tokens": estimated_tokens,
            "total_interactions": interaction_count,
            "needs_summarization": needs_summarization,
            "session_stats": self.get_session_stats(session_id)
        }
        
        # Perform summarization if needed
        if needs_summarization:
            summary_result = self._create_session_summary(session_id)
            result["summarization"] = summary_result
        
        return result
    
    def get_context(self, session_id: str, max_tokens: Optional[int] = None) -> Tuple[str, ContextStats]:
        """
        Get intelligent context with token awareness
        
        Args:
            session_id: Session identifier
            max_tokens: Maximum tokens to include (uses config default if None)
            
        Returns:
            Tuple of (context_string, context_stats)
        """
        max_tokens = max_tokens or self.config.max_context_tokens
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session summary if available
        cursor.execute('''
            SELECT summary_text, interactions_summarized, updated_at
            FROM session_summaries 
            WHERE session_id = ?
        ''', (session_id,))
        
        summary_row = cursor.fetchone()
        context_parts = []
        current_tokens = 0
        summarized_interactions = 0
        
        if summary_row:
            summary_text, summarized_interactions, _ = summary_row
            summary_tokens = len(summary_text) // 4
            if summary_tokens <= max_tokens * 0.3:  # Use max 30% of tokens for summary
                context_parts.append(f"[Previous conversation summary]: {summary_text}")
                current_tokens += summary_tokens
        
        # Get recent interactions (after summary)
        cursor.execute('''
            SELECT user_input, agent_output, estimated_tokens, timestamp
            FROM conversations 
            WHERE session_id = ? AND is_summarized = FALSE
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, self.config.max_interactions_per_session))
        
        recent_interactions = cursor.fetchall()
        raw_interactions = 0
        
        # Add recent interactions within token limit
        for user_input, agent_output, est_tokens, timestamp in reversed(recent_interactions):
            if current_tokens + est_tokens <= max_tokens:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                context_parts.append(f"User ({time_str}): {user_input}")
                context_parts.append(f"Agent ({time_str}): {agent_output}")
                current_tokens += est_tokens
                raw_interactions += 1
            else:
                break
        
        # Calculate session age
        cursor.execute('''
            SELECT MIN(timestamp) FROM conversations WHERE session_id = ?
        ''', (session_id,))
        
        first_interaction = cursor.fetchone()[0]
        session_age_hours = 0
        if first_interaction:
            session_start = datetime.fromisoformat(first_interaction)
            session_age_hours = (datetime.now() - session_start).total_seconds() / 3600
        
        conn.close()
        
        context_string = "\n".join(context_parts)
        stats = ContextStats(
            total_interactions=len(recent_interactions) + summarized_interactions,
            estimated_tokens=current_tokens,
            summarized_interactions=summarized_interactions,
            raw_interactions=raw_interactions,
            session_age_hours=session_age_hours
        )
        
        return context_string, stats
    
    def _create_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Create intelligent summary of older interactions
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summarization result
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get interactions to summarize (oldest unsummarized ones)
        cursor.execute('''
            SELECT id, user_input, agent_output, timestamp
            FROM conversations 
            WHERE session_id = ? AND is_summarized = FALSE
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (session_id, self.config.summarization_threshold))
        
        interactions = cursor.fetchall()
        
        if len(interactions) < self.config.summarization_threshold:
            conn.close()
            return {"summarized": False, "reason": "insufficient_interactions"}
        
        # Create summary text
        summary_parts = []
        interaction_ids = []
        
        for interaction_id, user_input, agent_output, timestamp in interactions:
            # Create concise summary of each interaction
            summary_parts.append(f"User asked: {user_input[:100]}...")
            summary_parts.append(f"Agent responded: {agent_output[:200]}...")
            interaction_ids.append(interaction_id)
        
        summary_text = " | ".join(summary_parts)
        
        # Store or update session summary
        cursor.execute('''
            INSERT OR REPLACE INTO session_summaries 
            (session_id, summary_text, interactions_summarized, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (session_id, summary_text, len(interactions), datetime.now().isoformat()))
        
        # Mark interactions as summarized
        cursor.execute(f'''
            UPDATE conversations 
            SET is_summarized = TRUE 
            WHERE id IN ({','.join(['?'] * len(interaction_ids))})
        ''', interaction_ids)
        
        conn.commit()
        conn.close()
        
        return {
            "summarized": True,
            "interactions_count": len(interactions),
            "summary_length": len(summary_text),
            "summary_preview": summary_text[:100] + "..."
        }
    
    def cleanup_old_sessions(self, hours_threshold: Optional[int] = None) -> Dict[str, Any]:
        """
        Clean up old sessions to prevent database bloat
        
        Args:
            hours_threshold: Hours after which to clean sessions
            
        Returns:
            Cleanup results
        """
        hours_threshold = hours_threshold or self.config.session_timeout_hours
        cutoff_time = datetime.now() - timedelta(hours=hours_threshold)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find old sessions
        cursor.execute('''
            SELECT DISTINCT session_id, MIN(timestamp) as first_interaction
            FROM conversations 
            GROUP BY session_id
            HAVING datetime(first_interaction) < ?
        ''', (cutoff_time.isoformat(),))
        
        old_sessions = cursor.fetchall()
        
        cleaned_sessions = []
        for session_id, first_interaction in old_sessions:
            # Keep summary but remove detailed interactions
            cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM memory_stats WHERE session_id = ?', (session_id,))
            cleaned_sessions.append(session_id)
        
        conn.commit()
        conn.close()
        
        return {
            "cleaned_sessions": len(cleaned_sessions),
            "session_ids": cleaned_sessions,
            "cutoff_hours": hours_threshold
        }
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute('''
            SELECT 
                COUNT(*) as interaction_count,
                SUM(estimated_tokens) as total_tokens,
                MIN(timestamp) as first_interaction,
                MAX(timestamp) as last_interaction
            FROM conversations 
            WHERE session_id = ?
        ''', (session_id,))
        
        stats = cursor.fetchone()
        
        # Get summary info
        cursor.execute('''
            SELECT interactions_summarized 
            FROM session_summaries 
            WHERE session_id = ?
        ''', (session_id,))
        
        summary_info = cursor.fetchone()
        
        conn.close()
        
        if not stats or not stats[0]:
            return {"exists": False}
        
        interaction_count, total_tokens, first_time, last_time = stats
        
        return {
            "exists": True,
            "interaction_count": interaction_count,
            "total_tokens": total_tokens or 0,
            "summarized_interactions": summary_info[0] if summary_info else 0,
            "session_age_hours": (datetime.now() - datetime.fromisoformat(first_time)).total_seconds() / 3600,
            "last_activity": last_time,
            "estimated_cost": (total_tokens or 0) * 0.00002  # Rough estimate: $0.02 per 1K tokens
        }
    
    def _update_session_stats(self, cursor, session_id: str, tokens_used: int):
        """Update session statistics"""
        cursor.execute('''
            INSERT OR REPLACE INTO memory_stats 
            (session_id, total_tokens_used, api_calls_made, last_updated)
            VALUES (
                ?, 
                COALESCE((SELECT total_tokens_used FROM memory_stats WHERE session_id = ?), 0) + ?,
                COALESCE((SELECT api_calls_made FROM memory_stats WHERE session_id = ?), 0) + 1,
                ?
            )
        ''', (session_id, session_id, tokens_used, session_id, datetime.now().isoformat()))
    
    def _get_interaction_count(self, cursor, session_id: str) -> int:
        """Get total interaction count for session"""
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE session_id = ?', (session_id,))
        return cursor.fetchone()[0]
    
    def get_memory_insights(self) -> Dict[str, Any]:
        """Get comprehensive memory system insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(*) as total_interactions,
                SUM(estimated_tokens) as total_tokens,
                AVG(estimated_tokens) as avg_tokens_per_interaction
            FROM conversations
        ''')
        
        overall_stats = cursor.fetchone()
        
        # Recent activity (last 24 hours)
        recent_cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT session_id) as active_sessions,
                COUNT(*) as recent_interactions,
                SUM(estimated_tokens) as recent_tokens
            FROM conversations
            WHERE timestamp > ?
        ''', (recent_cutoff,))
        
        recent_stats = cursor.fetchone()
        
        # Summarization stats
        cursor.execute('SELECT COUNT(*) FROM session_summaries')
        summarized_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "overall": {
                "total_sessions": overall_stats[0] or 0,
                "total_interactions": overall_stats[1] or 0,
                "total_tokens": overall_stats[2] or 0,
                "avg_tokens_per_interaction": round(overall_stats[3] or 0, 2)
            },
            "recent_24h": {
                "active_sessions": recent_stats[0] or 0,
                "interactions": recent_stats[1] or 0,
                "tokens_used": recent_stats[2] or 0
            },
            "summarization": {
                "sessions_with_summaries": summarized_sessions,
                "enabled": self.config.enable_summarization
            },
            "configuration": {
                "max_context_tokens": self.config.max_context_tokens,
                "summarization_threshold": self.config.summarization_threshold,
                "session_timeout_hours": self.config.session_timeout_hours
            }
        }
