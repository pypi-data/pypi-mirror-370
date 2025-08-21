"""
Slash Command Processor for Metis Agent

Handles parsing and execution of slash commands with multi-agent support.
"""

import re
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .registry import SlashCommandRegistry
from .metis_file_parser import MetisFileParser
from ..agent_commands import get_agent_manager


class SlashCommandProcessor:
    """Processes slash commands with context awareness and multi-agent support."""
    
    def __init__(self, config=None):
        self.registry = SlashCommandRegistry()
        self.metis_parser = MetisFileParser()
        self.config = config
        self.current_session = None
        
        # Load .metis file if present
        self._load_project_metis_file()
    
    def _load_project_metis_file(self):
        """Load .metis file from current directory if it exists."""
        metis_file = Path.cwd() / ".metis"
        if metis_file.exists():
            try:
                self.project_config = self.metis_parser.parse_file(metis_file)
            except Exception as e:
                print(f"Warning: Error loading .metis file: {e}")
                self.project_config = {}
        else:
            self.project_config = {}
    
    def is_slash_command(self, text: str) -> bool:
        """Check if text starts with a slash command."""
        return text.strip().startswith('/')
    
    def parse_command(self, text: str) -> Tuple[str, List[str], str]:
        """
        Parse slash command into command name, arguments, and remaining text.
        
        Returns:
            (command_name, args, remaining_text)
        """
        text = text.strip()
        if not text.startswith('/'):
            return None, [], text
        
        # Remove the leading slash
        text = text[1:]
        
        # Split into parts
        parts = text.split()
        if not parts:
            return None, [], ""
        
        command_name = parts[0]
        
        # Parse arguments and remaining text
        args = []
        remaining_parts = []
        in_args = True
        
        for part in parts[1:]:
            if in_args and part.startswith('-'):
                args.append(part)
            else:
                in_args = False
                remaining_parts.append(part)
        
        remaining_text = ' '.join(remaining_parts)
        
        return command_name, args, remaining_text
    
    async def execute_command(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a slash command with full context support.
        
        Args:
            text: The slash command text
            context: Additional context (session, agent, etc.)
            
        Returns:
            Dictionary with execution result
        """
        command_name, args, remaining_text = self.parse_command(text)
        
        if not command_name:
            return {"success": False, "error": "Invalid slash command"}
        
        # Check if command exists in registry
        if not self.registry.has_command(command_name):
            return {"success": False, "error": f"Unknown command: /{command_name}"}
        
        # Get command handler
        command_handler = self.registry.get_command(command_name)
        
        # Prepare execution context
        exec_context = {
            "command_name": command_name,
            "args": args,
            "remaining_text": remaining_text,
            "project_config": self.project_config,
            "session": context.get("session") if context else None,
            "current_agent": context.get("current_agent") if context else None,
            "agent_manager": self._get_agent_manager(),
            "config": self.config
        }
        
        try:
            # Execute the command
            result = await command_handler.execute(exec_context)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing /{command_name}: {str(e)}"
            }
    
    def _get_agent_manager(self):
        """Get agent manager if available."""
        try:
            return get_agent_manager()
        except Exception:
            return None
    
    def get_available_commands(self) -> List[str]:
        """Get list of all available slash commands."""
        return self.registry.list_commands()
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        """Get help text for a specific command."""
        if self.registry.has_command(command_name):
            command = self.registry.get_command(command_name)
            return command.get_help()
        return None
    
    def get_project_custom_instructions(self) -> str:
        """Get custom instructions from .metis file."""
        return self.project_config.get("instructions", "")
    
    def get_project_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration from .metis file."""
        return self.project_config.get("agent", {})
    
    def reload_project_config(self):
        """Reload .metis file configuration."""
        self._load_project_metis_file()