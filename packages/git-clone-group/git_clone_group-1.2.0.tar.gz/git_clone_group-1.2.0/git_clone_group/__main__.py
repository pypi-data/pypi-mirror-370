"""
Main entry point for running git_clone_group as a module.

This allows the package to be executed with `python -m git_clone_group`.
"""

from .cli import cli

if __name__ == "__main__":
    cli()
