"""
Main entry point for Metis Agent CLI.

This allows running the CLI with 'python -m metis_agent'.
"""

from .cli.commands import cli

if __name__ == "__main__":
    cli()
