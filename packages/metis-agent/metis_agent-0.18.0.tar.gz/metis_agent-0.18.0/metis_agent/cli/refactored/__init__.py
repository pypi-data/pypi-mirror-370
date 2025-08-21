"""
Refactored CLI module with modular architecture.

This package contains the refactored CLI components broken down into focused modules:
- command_router: Main command routing and entry points
- project_handlers: Project creation and management
- session_managers: Interactive session handling
- request_processors: Natural language request processing
- interface_adapters: Different interface modes (simple, advanced, expert)
- streaming_handlers: Streaming interface management
"""

from .command_router import code_command_group
from .project_handlers import ProjectHandler
from .session_managers import SessionManager
from .request_processors import RequestProcessor
from .interface_adapters import InterfaceAdapter
from .streaming_handlers import StreamingHandler

__all__ = [
    'code_command_group',
    'ProjectHandler', 
    'SessionManager',
    'RequestProcessor',
    'InterfaceAdapter',
    'StreamingHandler'
]