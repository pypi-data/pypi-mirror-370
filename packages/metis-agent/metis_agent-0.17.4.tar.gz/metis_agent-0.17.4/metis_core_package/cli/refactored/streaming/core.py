"""
Core streaming interface functionality.

Main streaming interface class with session management and coordination.
"""
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator

from .processors import StreamProcessor
from .handlers import StreamingEventHandler  
from .formatters import StreamingFormatter
from .permissions import PermissionManager
from .language_detection import LanguageDetector
from .session_management import StreamingSessionManager


class StreamingInterface:
    """Modern streaming interface with modular architecture."""
    
    def __init__(self, agent, project_location: str, tools_registry: Dict = None,
                 operation_mode: str = 'balanced', confirmation_level: str = 'normal',
                 interface_mode: str = 'simple'):
        """
        Initialize streaming interface.
        
        Args:
            agent: Agent instance for processing
            project_location: Location of the project
            tools_registry: Optional tools registry
            operation_mode: Operation mode (balanced, fast, detailed)
            confirmation_level: Confirmation level (minimal, normal, detailed)
            interface_mode: Interface mode (simple, advanced, expert)
        """
        self.agent = agent
        self.project_location = project_location
        self.tools_registry = tools_registry or {}
        self.operation_mode = operation_mode
        self.confirmation_level = confirmation_level
        self.interface_mode = interface_mode
        
        # Initialize components
        self.processor = StreamProcessor(self)
        self.event_handler = StreamingEventHandler(self)
        self.formatter = StreamingFormatter(self)
        self.permission_manager = PermissionManager(self)
        self.language_detector = LanguageDetector()
        self.session_manager = StreamingSessionManager(self)
        
        # Session state
        self.session_active = False
        self.session_id = None
        self.total_files_processed = 0
        self.total_lines_written = 0
        self.session_start_time = None
        
        # Status system integration
        self.status_manager = None
        self._initialize_status_system()
    
    def _initialize_status_system(self):
        """Initialize the status management system if available."""
        try:
            from ..status_manager import get_status_manager, StatusLevel
            self.status_manager = get_status_manager()
            if self.status_manager:
                self.status_manager.set_status(
                    StatusLevel.INFO,
                    "Streaming interface initialized",
                    details={
                        'project_location': self.project_location,
                        'operation_mode': self.operation_mode,
                        'interface_mode': self.interface_mode
                    }
                )
        except ImportError:
            pass  # Status system not available
    
    def start_session(self) -> Dict[str, Any]:
        """
        Start a new streaming session.
        
        Returns:
            Session information
        """
        session_info = self.session_manager.start_session()
        
        self.session_active = True
        self.session_id = session_info['session_id']
        self.session_start_time = time.time()
        
        # Show welcome message
        self.formatter.show_session_header(session_info)
        
        return session_info
    
    def stream_response(self, query: str, session_id: Optional[str] = None) -> Generator[str, None, None]:
        """
        Stream response for a query.
        
        Args:
            query: User query
            session_id: Optional session ID
            
        Yields:
            Response chunks
        """
        if not self.session_active:
            self.start_session()
        
        # Update status
        if self.status_manager:
            self.status_manager.set_status(
                "INFO", f"Processing query: {query[:50]}...",
                details={'session_id': self.session_id}
            )
        
        try:
            # Process query through agent
            response_generator = self.processor.process_query(query, session_id)
            
            # Stream the response
            for chunk in response_generator:
                yield chunk
                
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            if self.status_manager:
                self.status_manager.set_status("ERROR", error_msg)
            
            yield f"Error: {error_msg}\n"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if not self.session_active:
            return {'active': False}
        
        uptime = time.time() - self.session_start_time if self.session_start_time else 0
        
        return {
            'active': True,
            'session_id': self.session_id,
            'uptime_seconds': uptime,
            'files_processed': self.total_files_processed,
            'lines_written': self.total_lines_written,
            'project_location': self.project_location,
            'operation_mode': self.operation_mode,
            'interface_mode': self.interface_mode
        }
    
    def end_session(self):
        """End the current streaming session."""
        if self.session_active:
            session_stats = self.get_session_stats()
            self.formatter.show_session_footer(session_stats)
            
            self.session_manager.end_session()
            
            self.session_active = False
            self.session_id = None
            self.session_start_time = None
            
            if self.status_manager:
                self.status_manager.set_status(
                    "INFO", "Streaming session ended",
                    details=session_stats
                )
    
    def pause_session(self):
        """Pause the current session."""
        if self.session_active:
            self.session_manager.pause_session()
            self.formatter.show_pause_message()
    
    def resume_session(self):
        """Resume a paused session."""
        if self.session_active:
            self.session_manager.resume_session()
            self.formatter.show_resume_message()
    
    def get_project_context(self) -> Dict[str, Any]:
        """Get current project context information."""
        return {
            'location': self.project_location,
            'exists': os.path.exists(self.project_location),
            'is_git_repo': self._check_git_status()['is_git_repo'],
            'file_count': self._count_project_files(),
            'has_code_files': self._has_code_files()
        }
    
    def _check_git_status(self) -> Dict[str, Any]:
        """Check git repository status."""
        try:
            import subprocess
            
            # Check if in git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.project_location,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Get current branch
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    cwd=self.project_location,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Get status
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=self.project_location,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return {
                    'is_git_repo': True,
                    'current_branch': branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown',
                    'has_changes': bool(status_result.stdout.strip()) if status_result.returncode == 0 else False,
                    'status': 'clean' if not bool(status_result.stdout.strip()) else 'modified'
                }
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        return {
            'is_git_repo': False,
            'current_branch': None,
            'has_changes': False,
            'status': 'not_git'
        }
    
    def _count_project_files(self) -> int:
        """Count files in project directory."""
        try:
            if os.path.exists(self.project_location):
                return len([
                    f for f in os.listdir(self.project_location)
                    if os.path.isfile(os.path.join(self.project_location, f))
                ])
        except (PermissionError, OSError):
            pass
        
        return 0
    
    def _has_code_files(self) -> bool:
        """Check if project has code files."""
        code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'}
        
        try:
            if os.path.exists(self.project_location):
                for file in os.listdir(self.project_location):
                    if any(file.endswith(ext) for ext in code_extensions):
                        return True
        except (PermissionError, OSError):
            pass
        
        return False