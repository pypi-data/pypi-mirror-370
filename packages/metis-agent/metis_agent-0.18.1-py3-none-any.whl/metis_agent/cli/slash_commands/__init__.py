"""
Slash Commands System for Metis Agent

Provides Claude Code-style slash commands with multi-agent integration
and custom .metis file support for project-specific behaviors.
"""

from .processor import SlashCommandProcessor
from .registry import SlashCommandRegistry
from .metis_file_parser import MetisFileParser
from .built_in_commands import register_built_in_commands

__all__ = [
    'SlashCommandProcessor',
    'SlashCommandRegistry', 
    'MetisFileParser',
    'register_built_in_commands'
]