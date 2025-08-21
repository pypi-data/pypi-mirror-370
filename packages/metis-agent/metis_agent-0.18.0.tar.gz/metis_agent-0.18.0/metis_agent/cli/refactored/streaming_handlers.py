"""
Streaming interface handlers for real-time CLI interactions.

Handles streaming sessions, real-time updates, and interactive feedback.
"""
import asyncio
import time
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class StreamingState(Enum):
    """Streaming session states."""
    IDLE = "idle"
    INITIALIZING = "initializing"  
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING_INPUT = "waiting_input"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class StreamingMessage:
    """Message in streaming interface."""
    timestamp: float
    type: str  # 'user', 'agent', 'system', 'progress'
    content: str
    metadata: Dict[str, Any] = None


class StreamingHandler:
    """Handles streaming interface sessions."""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def create_streaming_session(self, session_id: str, 
                               project_location: str,
                               config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new streaming session.
        
        Args:
            session_id: Unique session identifier
            project_location: Location of the project
            config: Optional configuration
            
        Returns:
            Session information
        """
        session_config = {
            'buffer_size': 1000,
            'update_interval': 0.1,
            'auto_save': True,
            'show_progress': True,
            'enable_rich': True,
            **(config or {})
        }
        
        session_info = {
            'session_id': session_id,
            'project_location': project_location,
            'state': StreamingState.INITIALIZING,
            'created_at': time.time(),
            'last_activity': time.time(),
            'message_buffer': [],
            'progress_data': {},
            'config': session_config,
            'metadata': {
                'total_messages': 0,
                'user_messages': 0,
                'agent_responses': 0,
                'errors': 0
            }
        }
        
        self.active_streams[session_id] = session_info
        return session_info
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get streaming session by ID."""
        return self.active_streams.get(session_id)
    
    def update_session_state(self, session_id: str, new_state: StreamingState,
                           metadata: Dict = None):
        """Update session state."""
        if session_id in self.active_streams:
            session = self.active_streams[session_id]
            session['state'] = new_state
            session['last_activity'] = time.time()
            
            if metadata:
                session['metadata'].update(metadata)
    
    def add_message(self, session_id: str, message_type: str, 
                   content: str, metadata: Dict = None) -> bool:
        """
        Add message to streaming session.
        
        Args:
            session_id: Session ID
            message_type: Type of message ('user', 'agent', 'system', 'progress')
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        if session_id not in self.active_streams:
            return False
        
        session = self.active_streams[session_id]
        message = StreamingMessage(
            timestamp=time.time(),
            type=message_type,
            content=content,
            metadata=metadata or {}
        )
        
        # Add to buffer
        session['message_buffer'].append(message)
        
        # Update metadata
        session['metadata']['total_messages'] += 1
        if message_type == 'user':
            session['metadata']['user_messages'] += 1
        elif message_type == 'agent':
            session['metadata']['agent_responses'] += 1
        elif message_type == 'error':
            session['metadata']['errors'] += 1
        
        # Maintain buffer size
        buffer_size = session['config']['buffer_size']
        if len(session['message_buffer']) > buffer_size:
            session['message_buffer'] = session['message_buffer'][-buffer_size:]
        
        # Trigger message handler if registered
        if session_id in self.message_handlers:
            try:
                self.message_handlers[session_id](message)
            except Exception as e:
                print(f"Message handler error: {e}")
        
        session['last_activity'] = time.time()
        return True
    
    def get_messages(self, session_id: str, limit: int = None, 
                    message_type: str = None) -> list:
        """
        Get messages from session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages
            message_type: Filter by message type
            
        Returns:
            List of messages
        """
        if session_id not in self.active_streams:
            return []
        
        messages = self.active_streams[session_id]['message_buffer']
        
        # Filter by type if specified
        if message_type:
            messages = [msg for msg in messages if msg.type == message_type]
        
        # Apply limit
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def update_progress(self, session_id: str, progress_data: Dict):
        """Update progress information for session."""
        if session_id not in self.active_streams:
            return
        
        session = self.active_streams[session_id]
        session['progress_data'].update(progress_data)
        session['last_activity'] = time.time()
        
        # Trigger progress callback if registered
        if session_id in self.progress_callbacks:
            try:
                self.progress_callbacks[session_id](progress_data)
            except Exception as e:
                print(f"Progress callback error: {e}")
    
    def register_message_handler(self, session_id: str, 
                                handler: Callable[[StreamingMessage], None]):
        """Register message handler for session."""
        self.message_handlers[session_id] = handler
    
    def register_progress_callback(self, session_id: str,
                                 callback: Callable[[Dict], None]):
        """Register progress callback for session."""
        self.progress_callbacks[session_id] = callback
    
    async def stream_response(self, session_id: str, 
                            response_generator: AsyncGenerator[str, None],
                            response_type: str = 'agent') -> bool:
        """
        Stream response content to session.
        
        Args:
            session_id: Session ID
            response_generator: Async generator yielding response chunks
            response_type: Type of response
            
        Returns:
            Success status
        """
        if session_id not in self.active_streams:
            return False
        
        try:
            accumulated_content = ""
            chunk_count = 0
            
            async for chunk in response_generator:
                if chunk:
                    accumulated_content += chunk
                    chunk_count += 1
                    
                    # Send intermediate updates for long responses
                    if chunk_count % 10 == 0:  # Every 10 chunks
                        self.add_message(
                            session_id, 
                            'progress',
                            f"Streaming response... ({len(accumulated_content)} chars)",
                            {'chunk_count': chunk_count, 'partial_content': True}
                        )
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.01)
            
            # Add final complete message
            if accumulated_content:
                self.add_message(
                    session_id,
                    response_type,
                    accumulated_content,
                    {'chunk_count': chunk_count, 'streaming_complete': True}
                )
            
            return True
        
        except Exception as e:
            self.add_message(
                session_id,
                'error',
                f"Streaming error: {str(e)}",
                {'error_type': 'streaming_error'}
            )
            return False
    
    def format_session_display(self, session_id: str, 
                             include_progress: bool = True) -> str:
        """
        Format session information for display.
        
        Args:
            session_id: Session ID
            include_progress: Whether to include progress information
            
        Returns:
            Formatted session display
        """
        if session_id not in self.active_streams:
            return f"Session {session_id} not found"
        
        session = self.active_streams[session_id]
        
        display_parts = []
        
        # Header
        display_parts.append(f"Streaming Session: {session_id}")
        display_parts.append(f"State: {session['state'].value}")
        display_parts.append(f"Project: {session['project_location']}")
        
        # Statistics
        meta = session['metadata']
        display_parts.append(f"Messages: {meta['total_messages']} "
                           f"(User: {meta['user_messages']}, "
                           f"Agent: {meta['agent_responses']}, "
                           f"Errors: {meta['errors']})")
        
        # Progress information
        if include_progress and session['progress_data']:
            display_parts.append("Progress:")
            for key, value in session['progress_data'].items():
                display_parts.append(f"  {key}: {value}")
        
        # Recent messages
        recent_messages = self.get_messages(session_id, limit=5)
        if recent_messages:
            display_parts.append("\nRecent Messages:")
            for msg in recent_messages:
                timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
                display_parts.append(f"  [{timestamp}] {msg.type}: {msg.content[:100]}...")
        
        return "\n".join(display_parts)
    
    def get_session_stats(self, session_id: str = None) -> Dict[str, Any]:
        """
        Get statistics for session(s).
        
        Args:
            session_id: Specific session ID, or None for all sessions
            
        Returns:
            Session statistics
        """
        if session_id:
            if session_id not in self.active_streams:
                return {}
            
            session = self.active_streams[session_id]
            return {
                'session_id': session_id,
                'state': session['state'].value,
                'uptime': time.time() - session['created_at'],
                'last_activity_ago': time.time() - session['last_activity'],
                'message_buffer_size': len(session['message_buffer']),
                **session['metadata']
            }
        
        else:
            # Statistics for all sessions
            total_sessions = len(self.active_streams)
            active_sessions = sum(
                1 for session in self.active_streams.values()
                if session['state'] in [StreamingState.ACTIVE, StreamingState.PROCESSING]
            )
            
            total_messages = sum(
                session['metadata']['total_messages']
                for session in self.active_streams.values()
            )
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'total_messages': total_messages,
                'sessions': list(self.active_streams.keys())
            }
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up streaming session."""
        if session_id in self.active_streams:
            # Clean up handlers
            self.message_handlers.pop(session_id, None)
            self.progress_callbacks.pop(session_id, None)
            
            # Remove session
            del self.active_streams[session_id]
            return True
        
        return False
    
    def cleanup_inactive_sessions(self, timeout_seconds: int = 3600) -> int:
        """
        Clean up sessions that have been inactive for specified timeout.
        
        Args:
            timeout_seconds: Inactivity timeout in seconds
            
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        inactive_sessions = []
        
        for session_id, session in self.active_streams.items():
            if (current_time - session['last_activity']) > timeout_seconds:
                inactive_sessions.append(session_id)
        
        cleaned_count = 0
        for session_id in inactive_sessions:
            if self.cleanup_session(session_id):
                cleaned_count += 1
        
        return cleaned_count
    
    def export_session(self, session_id: str, format: str = 'json') -> Optional[str]:
        """
        Export session data.
        
        Args:
            session_id: Session ID to export
            format: Export format ('json', 'text')
            
        Returns:
            Exported data as string, or None if session not found
        """
        if session_id not in self.active_streams:
            return None
        
        session = self.active_streams[session_id]
        
        if format == 'json':
            import json
            # Convert non-serializable objects
            export_data = {
                'session_id': session_id,
                'state': session['state'].value,
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'metadata': session['metadata'],
                'config': session['config'],
                'messages': [
                    {
                        'timestamp': msg.timestamp,
                        'type': msg.type,
                        'content': msg.content,
                        'metadata': msg.metadata
                    }
                    for msg in session['message_buffer']
                ]
            }
            return json.dumps(export_data, indent=2)
        
        elif format == 'text':
            lines = []
            lines.append(f"Streaming Session Export: {session_id}")
            lines.append(f"Created: {datetime.fromtimestamp(session['created_at'])}")
            lines.append(f"State: {session['state'].value}")
            lines.append("=" * 50)
            
            for msg in session['message_buffer']:
                timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[{timestamp}] {msg.type.upper()}: {msg.content}")
            
            return "\n".join(lines)
        
        return None