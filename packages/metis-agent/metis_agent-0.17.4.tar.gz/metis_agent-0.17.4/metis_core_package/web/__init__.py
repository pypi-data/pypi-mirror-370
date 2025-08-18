"""
Web package for Metis Agent.

This package provides a web server for interacting with the agent.
"""
from .output_formatter import format_response_for_frontend, extract_code_blocks, extract_tasks

__all__ = [
    'format_response_for_frontend',
    'extract_code_blocks',
    'extract_tasks'
]