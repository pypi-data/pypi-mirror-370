"""
Event handlers for streaming interface.

Handles events, callbacks, and state management during streaming operations.
"""
import time
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Types of streaming events."""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SESSION_PAUSE = "session_pause"
    SESSION_RESUME = "session_resume"
    QUERY_START = "query_start"
    QUERY_END = "query_end"
    FILE_CREATE_START = "file_create_start"
    FILE_CREATE_SUCCESS = "file_create_success"
    FILE_CREATE_ERROR = "file_create_error"
    PERMISSION_REQUEST = "permission_request"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class StreamingEvent:
    """Represents a streaming event."""
    event_type: EventType
    timestamp: float
    data: Dict[str, Any]
    session_id: Optional[str] = None


class StreamingEventHandler:
    """Handles streaming events and callbacks."""
    
    def __init__(self, interface):
        """Initialize with reference to main interface."""
        self.interface = interface
        self.event_history: List[StreamingEvent] = []
        self.event_callbacks: Dict[EventType, List[Callable]] = {}
        self.statistics = {
            'events_processed': 0,
            'errors': 0,
            'warnings': 0,
            'files_created': 0,
            'permissions_requested': 0,
            'permissions_granted': 0,
            'permissions_denied': 0,
        }
    
    def emit_event(self, event_type: EventType, data: Dict[str, Any] = None,
                   session_id: Optional[str] = None):
        """
        Emit a streaming event.
        
        Args:
            event_type: Type of event
            data: Event data
            session_id: Optional session ID
        """
        event = StreamingEvent(
            event_type=event_type,
            timestamp=time.time(),
            data=data or {},
            session_id=session_id or self.interface.session_id
        )
        
        # Add to history
        self.event_history.append(event)
        
        # Update statistics
        self._update_statistics(event)
        
        # Call registered callbacks
        self._call_event_callbacks(event)
        
        # Handle built-in event processing
        self._handle_builtin_event(event)
    
    def register_callback(self, event_type: EventType, callback: Callable[[StreamingEvent], None]):
        """
        Register callback for specific event type.
        
        Args:
            event_type: Event type to listen for
            callback: Callback function
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: EventType, callback: Callable):
        """Unregister a callback."""
        if event_type in self.event_callbacks:
            try:
                self.event_callbacks[event_type].remove(callback)
            except ValueError:
                pass  # Callback not found
    
    def _update_statistics(self, event: StreamingEvent):
        """Update statistics based on event."""
        self.statistics['events_processed'] += 1
        
        if event.event_type == EventType.ERROR:
            self.statistics['errors'] += 1
        elif event.event_type == EventType.WARNING:
            self.statistics['warnings'] += 1
        elif event.event_type == EventType.FILE_CREATE_SUCCESS:
            self.statistics['files_created'] += 1
        elif event.event_type == EventType.PERMISSION_REQUEST:
            self.statistics['permissions_requested'] += 1
        elif event.event_type == EventType.PERMISSION_GRANTED:
            self.statistics['permissions_granted'] += 1
        elif event.event_type == EventType.PERMISSION_DENIED:
            self.statistics['permissions_denied'] += 1
    
    def _call_event_callbacks(self, event: StreamingEvent):
        """Call registered callbacks for event type."""
        callbacks = self.event_callbacks.get(event.event_type, [])
        
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                # Don't let callback errors break the system
                self.emit_event(
                    EventType.ERROR,
                    {'message': f"Callback error: {str(e)}", 'callback': str(callback)}
                )
    
    def _handle_builtin_event(self, event: StreamingEvent):
        """Handle built-in event processing."""
        # Update status system if available
        if self.interface.status_manager:
            self._update_status_system(event)
        
        # Log important events
        if event.event_type in [EventType.ERROR, EventType.WARNING]:
            self._log_event(event)
    
    def _update_status_system(self, event: StreamingEvent):
        """Update status system based on event."""
        try:
            from ..status_manager import StatusLevel
            
            status_mapping = {
                EventType.ERROR: StatusLevel.ERROR,
                EventType.WARNING: StatusLevel.WARNING,
                EventType.INFO: StatusLevel.INFO,
                EventType.SESSION_START: StatusLevel.SUCCESS,
                EventType.SESSION_END: StatusLevel.SUCCESS,
                EventType.FILE_CREATE_SUCCESS: StatusLevel.SUCCESS,
                EventType.FILE_CREATE_ERROR: StatusLevel.ERROR,
                EventType.PERMISSION_DENIED: StatusLevel.WARNING,
            }
            
            status_level = status_mapping.get(event.event_type)
            if status_level:
                message = self._format_event_message(event)
                self.interface.status_manager.set_status(
                    status_level, message, details=event.data
                )
        except ImportError:
            pass  # Status system not available
    
    def _format_event_message(self, event: StreamingEvent) -> str:
        """Format event as status message."""
        message_templates = {
            EventType.SESSION_START: "Streaming session started",
            EventType.SESSION_END: "Streaming session ended",
            EventType.SESSION_PAUSE: "Session paused",
            EventType.SESSION_RESUME: "Session resumed",
            EventType.QUERY_START: "Processing query: {query}",
            EventType.QUERY_END: "Query completed",
            EventType.FILE_CREATE_START: "Creating file: {filename}",
            EventType.FILE_CREATE_SUCCESS: "Successfully created: {filename}",
            EventType.FILE_CREATE_ERROR: "Failed to create: {filename}",
            EventType.PERMISSION_REQUEST: "Permission requested for: {operation}",
            EventType.PERMISSION_GRANTED: "Permission granted for: {operation}",
            EventType.PERMISSION_DENIED: "Permission denied for: {operation}",
            EventType.ERROR: "Error: {message}",
            EventType.WARNING: "Warning: {message}",
            EventType.INFO: "Info: {message}",
        }
        
        template = message_templates.get(event.event_type, str(event.event_type))
        
        try:
            return template.format(**event.data)
        except (KeyError, ValueError):
            return template
    
    def _log_event(self, event: StreamingEvent):
        """Log important events."""
        # Simple console logging for now
        timestamp_str = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
        
        if event.event_type == EventType.ERROR:
            print(f"[{timestamp_str}] ERROR: {event.data.get('message', 'Unknown error')}")
        elif event.event_type == EventType.WARNING:
            print(f"[{timestamp_str}] WARNING: {event.data.get('message', 'Unknown warning')}")
    
    def get_events(self, event_type: Optional[EventType] = None,
                   session_id: Optional[str] = None,
                   limit: Optional[int] = None) -> List[StreamingEvent]:
        """
        Get events with optional filtering.
        
        Args:
            event_type: Filter by event type
            session_id: Filter by session ID
            limit: Maximum number of events to return
            
        Returns:
            Filtered list of events
        """
        events = self.event_history
        
        # Filter by event type
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Filter by session ID
        if session_id:
            events = [e for e in events if e.session_id == session_id]
        
        # Apply limit
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics."""
        return self.statistics.copy()
    
    def clear_history(self, older_than_seconds: Optional[int] = None):
        """
        Clear event history.
        
        Args:
            older_than_seconds: Only clear events older than this many seconds
        """
        if older_than_seconds:
            cutoff_time = time.time() - older_than_seconds
            self.event_history = [
                event for event in self.event_history
                if event.timestamp > cutoff_time
            ]
        else:
            self.event_history.clear()
    
    def get_session_events(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary of events for a specific session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session event summary
        """
        session_events = [e for e in self.event_history if e.session_id == session_id]
        
        if not session_events:
            return {'session_id': session_id, 'events': [], 'summary': {}}
        
        # Calculate session summary
        event_counts = {}
        for event in session_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        start_time = min(event.timestamp for event in session_events)
        end_time = max(event.timestamp for event in session_events)
        
        return {
            'session_id': session_id,
            'events': session_events,
            'summary': {
                'total_events': len(session_events),
                'event_counts': event_counts,
                'duration_seconds': end_time - start_time,
                'start_time': start_time,
                'end_time': end_time,
            }
        }
    
    def export_events(self, format: str = 'json', 
                     session_id: Optional[str] = None) -> str:
        """
        Export events to various formats.
        
        Args:
            format: Export format ('json', 'csv', 'text')
            session_id: Optional session ID filter
            
        Returns:
            Exported events as string
        """
        events = self.get_events(session_id=session_id)
        
        if format == 'json':
            import json
            
            export_data = []
            for event in events:
                export_data.append({
                    'timestamp': event.timestamp,
                    'event_type': event.event_type.value,
                    'session_id': event.session_id,
                    'data': event.data
                })
            
            return json.dumps(export_data, indent=2)
        
        elif format == 'csv':
            lines = ['timestamp,event_type,session_id,data']
            
            for event in events:
                data_str = str(event.data).replace(',', ';')  # Simple CSV escape
                lines.append(f"{event.timestamp},{event.event_type.value},{event.session_id},{data_str}")
            
            return '\n'.join(lines)
        
        elif format == 'text':
            lines = []
            
            for event in events:
                timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.timestamp))
                lines.append(f"[{timestamp_str}] {event.event_type.value}: {event.data}")
            
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    # Convenience methods for common events
    
    def on_session_start(self, session_id: str):
        """Handle session start event."""
        self.emit_event(EventType.SESSION_START, {'session_id': session_id}, session_id)
    
    def on_session_end(self, session_id: str, statistics: Dict[str, Any]):
        """Handle session end event."""
        self.emit_event(EventType.SESSION_END, statistics, session_id)
    
    def on_query_start(self, query: str, session_id: str = None):
        """Handle query start event."""
        self.emit_event(EventType.QUERY_START, {'query': query}, session_id)
    
    def on_query_end(self, query: str, result: Any, session_id: str = None):
        """Handle query end event."""
        self.emit_event(EventType.QUERY_END, {'query': query, 'result': str(result)}, session_id)
    
    def on_file_create_start(self, filename: str, session_id: str = None):
        """Handle file creation start event."""
        self.emit_event(EventType.FILE_CREATE_START, {'filename': filename}, session_id)
    
    def on_file_create_success(self, filename: str, path: str, session_id: str = None):
        """Handle file creation success event."""
        self.emit_event(EventType.FILE_CREATE_SUCCESS, {'filename': filename, 'path': path}, session_id)
    
    def on_file_create_error(self, filename: str, error: str, session_id: str = None):
        """Handle file creation error event."""
        self.emit_event(EventType.FILE_CREATE_ERROR, {'filename': filename, 'error': error}, session_id)
    
    def on_permission_request(self, operation: str, details: Dict[str, Any], session_id: str = None):
        """Handle permission request event."""
        data = {'operation': operation}
        data.update(details)
        self.emit_event(EventType.PERMISSION_REQUEST, data, session_id)
    
    def on_permission_granted(self, operation: str, session_id: str = None):
        """Handle permission granted event."""
        self.emit_event(EventType.PERMISSION_GRANTED, {'operation': operation}, session_id)
    
    def on_permission_denied(self, operation: str, reason: str = None, session_id: str = None):
        """Handle permission denied event."""
        data = {'operation': operation}
        if reason:
            data['reason'] = reason
        self.emit_event(EventType.PERMISSION_DENIED, data, session_id)
    
    def on_error(self, message: str, details: Dict[str, Any] = None, session_id: str = None):
        """Handle error event."""
        data = {'message': message}
        if details:
            data.update(details)
        self.emit_event(EventType.ERROR, data, session_id)
    
    def on_warning(self, message: str, details: Dict[str, Any] = None, session_id: str = None):
        """Handle warning event."""
        data = {'message': message}
        if details:
            data.update(details)
        self.emit_event(EventType.WARNING, data, session_id)