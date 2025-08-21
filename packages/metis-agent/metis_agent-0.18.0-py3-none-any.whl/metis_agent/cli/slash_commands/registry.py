"""
Slash Command Registry

Manages registration and lookup of slash commands.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class SlashCommand(ABC):
    """Base class for all slash commands."""
    
    def __init__(self, name: str, description: str, usage: str = None):
        self.name = name
        self.description = description
        self.usage = usage or f"/{name}"
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the command with given context."""
        pass
    
    def get_help(self) -> str:
        """Get help text for this command."""
        help_text = f"/{self.name} - {self.description}\n"
        help_text += f"Usage: {self.usage}"
        return help_text


class SlashCommandRegistry:
    """Registry for managing slash commands."""
    
    def __init__(self):
        self.commands: Dict[str, SlashCommand] = {}
        self.aliases: Dict[str, str] = {}
    
    def register(self, command: SlashCommand, aliases: List[str] = None):
        """Register a slash command with optional aliases."""
        self.commands[command.name] = command
        
        if aliases:
            for alias in aliases:
                self.aliases[alias] = command.name
    
    def has_command(self, name: str) -> bool:
        """Check if a command exists."""
        return name in self.commands or name in self.aliases
    
    def get_command(self, name: str) -> Optional[SlashCommand]:
        """Get a command by name or alias."""
        # Check direct command name
        if name in self.commands:
            return self.commands[name]
        
        # Check aliases
        if name in self.aliases:
            actual_name = self.aliases[name]
            return self.commands.get(actual_name)
        
        return None
    
    def list_commands(self) -> List[str]:
        """Get list of all command names."""
        return list(self.commands.keys())
    
    def get_commands_by_category(self) -> Dict[str, List[str]]:
        """Get commands organized by category."""
        categories = {
            "General": [],
            "Development": [],
            "Agent Management": [],
            "Project": [],
            "Custom": []
        }
        
        for name, command in self.commands.items():
            # Categorize based on command type or name patterns
            if hasattr(command, 'category'):
                category = command.category
            elif name in ['help', 'clear', 'exit']:
                category = "General"
            elif name in ['review', 'test', 'deploy', 'commit']:
                category = "Development"
            elif name in ['agent', 'agents', 'mention']:
                category = "Agent Management"
            elif name in ['project', 'status', 'init']:
                category = "Project"
            else:
                category = "Custom"
            
            if category in categories:
                categories[category].append(name)
            else:
                categories["Custom"].append(name)
        
        return categories