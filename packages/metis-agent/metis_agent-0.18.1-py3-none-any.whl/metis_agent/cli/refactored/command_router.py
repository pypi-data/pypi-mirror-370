"""
Main command router for code intelligence CLI.

Handles the main entry point and routes requests to appropriate handlers.
"""
import click
from typing import Optional, Tuple

from .project_handlers import ProjectHandler
from .session_managers import SessionManager
from .request_processors import RequestProcessor
from .interface_adapters import InterfaceAdapter


class CommandRouter:
    """Routes CLI commands to appropriate handlers."""
    
    def __init__(self):
        self.project_handler = ProjectHandler()
        self.session_manager = SessionManager()
        self.request_processor = RequestProcessor()
        self.interface_adapter = InterfaceAdapter()
    
    def route_request(self, request, session=None, branch=None, no_branch=False, 
                     auto=False, fast=False, stream=False, yes=False, 
                     review=False, interface=None):
        """Route a request to the appropriate handler."""
        
        # Determine interface mode
        interface_mode = self.interface_adapter.determine_mode(
            interface, fast, stream, auto, review
        )
        
        # Process based on request type
        if not request:
            return self._handle_interactive_mode(
                session, branch, no_branch, interface_mode
            )
        
        # Join request text
        request_text = ' '.join(request)
        
        # Route to request processor
        return self.request_processor.process_request(
            request_text,
            session=session,
            branch=branch,
            no_branch=no_branch,
            auto=auto,
            interface_mode=interface_mode
        )
    
    def _handle_interactive_mode(self, session, branch, no_branch, interface_mode):
        """Handle interactive mode when no request is provided."""
        if interface_mode == 'streaming':
            return self.session_manager.start_streaming_session(
                session, branch, no_branch
            )
        else:
            return self.session_manager.start_interactive_session(
                session, branch, no_branch, interface_mode
            )


# Global router instance
_router = CommandRouter()


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument('request', nargs=-1, required=False)
@click.option('--session', '-s', help='Session ID for context')
@click.option('--branch', '-b', type=str, help='Create specific named feature branch')
@click.option('--no-branch', is_flag=True, help='Skip automatic branch creation')
@click.option('--auto', '-a', is_flag=True, help='Auto mode - skip prompts and execute directly')
@click.option('--fast', is_flag=True, help='Fast mode - minimal interface for simple operations')
@click.option('--stream', is_flag=True, help='Streaming mode - full interface for complex operations')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmations and use smart defaults')
@click.option('--review', is_flag=True, help='Force review mode with detailed confirmations')
@click.option('--interface', type=click.Choice(['simple', 'advanced', 'expert']), 
             help='Set interface complexity level')
def code_command_group(ctx, request, session, branch, no_branch, auto, fast, 
                      stream, yes, review, interface):
    """
    Natural language code intelligence interface.
    
    Examples:
        metis code "create a Python calculator with tests"
        metis code "add error handling to the login function"
        metis code --stream "refactor this module for better performance"
    """
    return _router.route_request(
        request, session, branch, no_branch, auto, fast, 
        stream, yes, review, interface
    )


# Alias for backward compatibility
code = code_command_group