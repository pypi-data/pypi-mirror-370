"""
Session management for streaming interface.

Handles lifecycle management of streaming sessions.
"""
import uuid
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class SessionState(Enum):
    """Session states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SessionInfo:
    """Information about a streaming session."""
    session_id: str
    state: SessionState
    created_at: float
    last_activity: float
    project_location: str
    operation_mode: str
    interface_mode: str
    total_queries: int = 0
    total_files_created: int = 0
    total_errors: int = 0


class StreamingSessionManager:
    """Manages streaming session lifecycle."""
    
    def __init__(self, interface):
        """Initialize with reference to main interface."""
        self.interface = interface
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_history: List[SessionInfo] = []
        self.current_session: Optional[SessionInfo] = None
    
    def start_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new streaming session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            Session information
        """
        if not session_id:
            session_id = self._generate_session_id()
        
        # End current session if any
        if self.current_session:
            self.end_session()
        
        # Create new session
        session_info = SessionInfo(
            session_id=session_id,
            state=SessionState.INITIALIZING,
            created_at=time.time(),
            last_activity=time.time(),
            project_location=self.interface.project_location,
            operation_mode=self.interface.operation_mode,
            interface_mode=self.interface.interface_mode
        )
        
        # Register session
        self.active_sessions[session_id] = session_info
        self.current_session = session_info
        
        # Emit event
        self.interface.event_handler.on_session_start(session_id)
        
        # Update state to active
        self._update_session_state(session_id, SessionState.ACTIVE)
        
        return {
            'session_id': session_id,
            'state': session_info.state.value,
            'created_at': session_info.created_at,
            'project_location': session_info.project_location,
            'operation_mode': session_info.operation_mode,
            'interface_mode': session_info.interface_mode
        }
    
    def end_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End a streaming session.
        
        Args:
            session_id: Optional session ID (defaults to current)
            
        Returns:
            Final session statistics
        """
        if not session_id:
            session_id = self.current_session.session_id if self.current_session else None
        
        if not session_id or session_id not in self.active_sessions:
            return {}
        
        session_info = self.active_sessions[session_id]
        
        # Calculate final statistics
        duration = time.time() - session_info.created_at
        final_stats = {
            'session_id': session_id,
            'duration_seconds': duration,
            'total_queries': session_info.total_queries,
            'total_files_created': session_info.total_files_created,
            'total_errors': session_info.total_errors,
            'state': SessionState.COMPLETED.value
        }
        
        # Update session state
        self._update_session_state(session_id, SessionState.COMPLETED)
        
        # Move to history
        self.session_history.append(session_info)
        del self.active_sessions[session_id]
        
        # Clear current session if it's the one being ended
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session = None
        
        # Emit event
        self.interface.event_handler.on_session_end(session_id, final_stats)
        
        return final_stats
    
    def pause_session(self, session_id: Optional[str] = None) -> bool:
        """
        Pause a streaming session.
        
        Args:
            session_id: Optional session ID (defaults to current)
            
        Returns:
            True if successfully paused
        """
        if not session_id:
            session_id = self.current_session.session_id if self.current_session else None
        
        if not session_id or session_id not in self.active_sessions:
            return False
        
        session_info = self.active_sessions[session_id]
        
        if session_info.state != SessionState.ACTIVE:
            return False
        
        self._update_session_state(session_id, SessionState.PAUSED)
        
        # Emit event
        self.interface.event_handler.emit_event(
            self.interface.event_handler.EventType.SESSION_PAUSE,
            {'session_id': session_id}
        )
        
        return True
    
    def resume_session(self, session_id: Optional[str] = None) -> bool:
        """
        Resume a paused session.
        
        Args:
            session_id: Optional session ID (defaults to current)
            
        Returns:
            True if successfully resumed
        """
        if not session_id:
            session_id = self.current_session.session_id if self.current_session else None
        
        if not session_id or session_id not in self.active_sessions:
            return False
        
        session_info = self.active_sessions[session_id]
        
        if session_info.state != SessionState.PAUSED:
            return False
        
        self._update_session_state(session_id, SessionState.ACTIVE)
        
        # Emit event
        self.interface.event_handler.emit_event(
            self.interface.event_handler.EventType.SESSION_RESUME,
            {'session_id': session_id}
        )
        
        return True
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information by ID."""
        return self.active_sessions.get(session_id)
    
    def get_current_session(self) -> Optional[SessionInfo]:
        """Get current active session."""
        return self.current_session
    
    def update_session_activity(self, session_id: Optional[str] = None,
                               activity_data: Dict[str, Any] = None):
        """
        Update session activity.
        
        Args:
            session_id: Optional session ID (defaults to current)
            activity_data: Activity data to record
        """
        if not session_id:
            session_id = self.current_session.session_id if self.current_session else None
        
        if not session_id or session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        session_info.last_activity = time.time()
        
        # Update activity counters
        if activity_data:
            if 'query' in activity_data:
                session_info.total_queries += 1
            if 'file_created' in activity_data:
                session_info.total_files_created += 1
            if 'error' in activity_data:
                session_info.total_errors += 1
    
    def _update_session_state(self, session_id: str, new_state: SessionState):
        """Update session state."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].state = new_state
            self.active_sessions[session_id].last_activity = time.time()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"stream_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        sessions = []
        
        for session_info in self.active_sessions.values():
            sessions.append({
                'session_id': session_info.session_id,
                'state': session_info.state.value,
                'created_at': session_info.created_at,
                'last_activity': session_info.last_activity,
                'uptime': time.time() - session_info.created_at,
                'idle_time': time.time() - session_info.last_activity,
                'total_queries': session_info.total_queries,
                'total_files_created': session_info.total_files_created,
                'total_errors': session_info.total_errors
            })
        
        return sessions
    
    def get_session_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Optional session ID (defaults to current)
            
        Returns:
            Session statistics
        """
        if not session_id:
            session_id = self.current_session.session_id if self.current_session else None
        
        if not session_id:
            return {}
        
        # Check active sessions first
        session_info = self.active_sessions.get(session_id)
        
        # Check history if not found in active
        if not session_info:
            for hist_session in self.session_history:
                if hist_session.session_id == session_id:
                    session_info = hist_session
                    break
        
        if not session_info:
            return {}
        
        current_time = time.time()
        
        return {
            'session_id': session_info.session_id,
            'state': session_info.state.value,
            'created_at': session_info.created_at,
            'last_activity': session_info.last_activity,
            'duration_seconds': current_time - session_info.created_at,
            'idle_seconds': current_time - session_info.last_activity,
            'project_location': session_info.project_location,
            'operation_mode': session_info.operation_mode,
            'interface_mode': session_info.interface_mode,
            'total_queries': session_info.total_queries,
            'total_files_created': session_info.total_files_created,
            'total_errors': session_info.total_errors,
            'is_active': session_info.session_id in self.active_sessions
        }
    
    def cleanup_inactive_sessions(self, max_idle_seconds: int = 3600) -> int:
        """
        Clean up sessions that have been inactive for too long.
        
        Args:
            max_idle_seconds: Maximum idle time before cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        cleanup_sessions = []
        
        for session_id, session_info in self.active_sessions.items():
            idle_time = current_time - session_info.last_activity
            
            if idle_time > max_idle_seconds:
                cleanup_sessions.append(session_id)
        
        # Clean up inactive sessions
        cleaned_count = 0
        for session_id in cleanup_sessions:
            self.end_session(session_id)
            cleaned_count += 1
        
        return cleaned_count
    
    def export_session_data(self, session_id: str, format: str = 'json') -> Optional[str]:
        """
        Export session data.
        
        Args:
            session_id: Session ID to export
            format: Export format ('json', 'text')
            
        Returns:
            Exported session data
        """
        stats = self.get_session_statistics(session_id)
        if not stats:
            return None
        
        if format == 'json':
            import json
            return json.dumps(stats, indent=2)
        
        elif format == 'text':
            lines = []
            lines.append(f"Session Export: {session_id}")
            lines.append("=" * 50)
            
            for key, value in stats.items():
                if key.endswith('_at'):
                    # Format timestamps
                    value = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
                elif key.endswith('_seconds'):
                    # Format durations
                    value = f"{value:.1f}s"
                
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
            
            return '\n'.join(lines)
        
        return None
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global session statistics."""
        total_sessions = len(self.active_sessions) + len(self.session_history)
        
        # Calculate totals from all sessions
        total_queries = sum(s.total_queries for s in self.active_sessions.values())
        total_queries += sum(s.total_queries for s in self.session_history)
        
        total_files = sum(s.total_files_created for s in self.active_sessions.values())
        total_files += sum(s.total_files_created for s in self.session_history)
        
        total_errors = sum(s.total_errors for s in self.active_sessions.values())
        total_errors += sum(s.total_errors for s in self.session_history)
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': len(self.active_sessions),
            'completed_sessions': len(self.session_history),
            'total_queries_processed': total_queries,
            'total_files_created': total_files,
            'total_errors': total_errors,
            'current_session_id': self.current_session.session_id if self.current_session else None
        }