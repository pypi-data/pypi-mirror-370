"""
Phase 3 CLI commands for Metis Agent.
Consolidates git, project, and dependency management commands.
"""

import click
import os
from typing import Dict, Any

# Import functions from existing command modules
from .git_commands import add_git_commands as _add_git_commands
from .project_commands import add_project_commands as _add_project_commands  
from .deps_commands import add_deps_commands as _add_deps_commands


def add_git_commands(cli):
    """Add git commands to CLI (Phase 3)."""
    _add_git_commands(cli)


def add_project_commands(cli):
    """Add project commands to CLI (Phase 3)."""
    _add_project_commands(cli)


def add_deps_commands(cli):
    """Add dependency management commands to CLI (Phase 3)."""
    _add_deps_commands(cli)
