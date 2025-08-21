"""
Configuration module for Metis Agent.

Provides agent profile management, YAML-based configuration,
and profile inheritance capabilities.
"""

from .agent_profiles import (
    AgentProfile,
    ProfileManager,
    LLMConfig,
    ToolConfig,
    MemoryConfig,
    PerformanceConfig,
    PermissionsConfig,
    SharedResourcesConfig,
    get_profile_manager,
    configure_profile_manager
)

__all__ = [
    'AgentProfile',
    'ProfileManager',
    'LLMConfig',
    'ToolConfig',
    'MemoryConfig',
    'PerformanceConfig',
    'PermissionsConfig',
    'SharedResourcesConfig',
    'get_profile_manager',
    'configure_profile_manager'
]