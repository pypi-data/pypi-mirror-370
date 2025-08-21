"""
git_clone_group - A tool for cloning GitLab groups and their projects.

This package provides functionality to clone or update multiple repositories
from GitLab groups and their subgroups in parallel.
"""

from .config import GitLabConfig, ProjectStats
from .main import download_code, download_code_by_name
from .cli import cli
from .__version__ import __version__

__all__ = [
    "GitLabConfig",
    "ProjectStats",
    "download_code",
    "download_code_by_name",
    "cli",
    "__version__",
]
