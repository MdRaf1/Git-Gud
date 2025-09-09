"""
Git Gud - An AI-powered command-line assistant for safer Git usage.

This package provides a safe interface to Git operations with proactive
dangerous operation detection and user confirmation workflows.
"""

__version__ = "0.1.0"
__author__ = "Git Gud Team"
__email__ = "team@gitgud.dev"

from .cli import main

__all__ = ["main"]