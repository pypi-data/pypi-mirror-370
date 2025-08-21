"""
Session management for CLI interactions.

Handles different types of interactive sessions and their lifecycle.
"""
import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime


class SessionManager:
    """Manages interactive sessions and their state."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_history: Dict[str, list] = {}
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        self.active_sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'request_count': 0,
            'context': {},
            'mode': 'interactive'
        }
        
        self.session_history[session_id] = []
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.active_sessions.get(session_id)
    
    def update_session_activity(self, session_id: str, context: Dict = None):
        """Update session with new activity."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = datetime.now().isoformat()
            self.active_sessions[session_id]['request_count'] += 1
            
            if context:
                self.active_sessions[session_id]['context'].update(context)
    
    def add_to_history(self, session_id: str, request: str, response: str):
        """Add request/response to session history."""
        if session_id in self.session_history:
            self.session_history[session_id].append({
                'timestamp': datetime.now().isoformat(),
                'request': request,
                'response': response
            })
    
    def start_interactive_session(self, session_id: Optional[str] = None,
                                branch: Optional[str] = None,
                                no_branch: bool = False,
                                interface_mode: str = 'balanced') -> Dict:
        """
        Start an interactive coding session.
        
        Args:
            session_id: Optional session ID to resume
            branch: Optional branch to create/switch to
            no_branch: Skip branch creation
            interface_mode: Interface mode to use
            
        Returns:
            Session information
        """
        if not session_id:
            session_id = self.create_session()
        elif session_id not in self.active_sessions:
            self.create_session(session_id)
        
        session_info = {
            'session_id': session_id,
            'mode': 'interactive',
            'interface_mode': interface_mode,
            'branch_info': self._handle_branch_setup(branch, no_branch),
            'project_context': self._get_project_context()
        }
        
        # Update session state
        self.active_sessions[session_id].update({
            'mode': 'interactive',
            'interface_mode': interface_mode,
            'branch_info': session_info['branch_info']
        })
        
        return session_info
    
    def start_streaming_session(self, session_id: Optional[str] = None,
                               branch: Optional[str] = None,
                               no_branch: bool = False) -> Dict:
        """
        Start a streaming session.
        
        Args:
            session_id: Optional session ID to resume
            branch: Optional branch to create/switch to  
            no_branch: Skip branch creation
            
        Returns:
            Session information
        """
        if not session_id:
            session_id = self.create_session()
        elif session_id not in self.active_sessions:
            self.create_session(session_id)
        
        session_info = {
            'session_id': session_id,
            'mode': 'streaming',
            'interface_mode': 'streaming',
            'branch_info': self._handle_branch_setup(branch, no_branch),
            'project_context': self._get_project_context()
        }
        
        # Update session state
        self.active_sessions[session_id].update({
            'mode': 'streaming',
            'interface_mode': 'streaming',
            'branch_info': session_info['branch_info']
        })
        
        return session_info
    
    def _handle_branch_setup(self, branch: Optional[str], no_branch: bool) -> Dict:
        """Handle Git branch creation/switching."""
        branch_info = {
            'branch_requested': branch,
            'skip_branch_creation': no_branch,
            'current_branch': None,
            'new_branch_created': False,
            'git_available': False
        }
        
        try:
            import subprocess
            
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                branch_info['git_available'] = True
                
                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    branch_info['current_branch'] = result.stdout.strip()
                
                # Create new branch if requested and not skipped
                if branch and not no_branch:
                    result = subprocess.run(['git', 'checkout', '-b', branch],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        branch_info['new_branch_created'] = True
                        branch_info['current_branch'] = branch
        
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Git not available or timeout
            pass
        
        return branch_info
    
    def _get_project_context(self) -> Dict:
        """Get current project context information."""
        context = {
            'current_directory': os.getcwd(),
            'directory_name': os.path.basename(os.getcwd()),
            'files_present': False,
            'file_count': 0,
            'has_code_files': False
        }
        
        try:
            files = os.listdir(context['current_directory'])
            context['files_present'] = len(files) > 0
            context['file_count'] = len(files)
            
            # Check for code files
            code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'}
            context['has_code_files'] = any(
                any(f.endswith(ext) for ext in code_extensions) 
                for f in files if os.path.isfile(f)
            )
        
        except (PermissionError, OSError):
            pass
        
        return context
    
    def cleanup_session(self, session_id: str):
        """Clean up a session."""
        self.active_sessions.pop(session_id, None)
        # Keep history for potential resume
    
    def list_active_sessions(self) -> Dict[str, Dict]:
        """List all active sessions."""
        return self.active_sessions.copy()
    
    def get_session_stats(self) -> Dict:
        """Get statistics about sessions."""
        return {
            'active_sessions': len(self.active_sessions),
            'total_sessions': len(self.session_history),
            'total_requests': sum(
                session['request_count'] 
                for session in self.active_sessions.values()
            )
        }