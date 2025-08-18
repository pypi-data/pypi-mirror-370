"""
Refactored streaming interface module.

This package contains the modular streaming interface components:
- core: Core streaming interface functionality
- processors: Stream processing and formatting
- handlers: Event and message handlers  
- formatters: Output formatting for different content types
- permissions: Permission management for file operations
- language_detection: Language and file type detection
- session_management: Session lifecycle management
"""

from .core import StreamingInterface
from .processors import StreamProcessor
from .handlers import StreamingEventHandler
from .formatters import StreamingFormatter
from .permissions import PermissionManager
from .language_detection import LanguageDetector
from .session_management import StreamingSessionManager

# Factory function for backward compatibility
def create_streaming_session(agent, project_location: str, **kwargs):
    """Create a streaming session with the new architecture."""
    return StreamingInterface(agent, project_location, **kwargs)

__all__ = [
    'StreamingInterface',
    'StreamProcessor', 
    'StreamingEventHandler',
    'StreamingFormatter',
    'PermissionManager',
    'LanguageDetector',
    'StreamingSessionManager',
    'create_streaming_session'
]