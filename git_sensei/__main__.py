"""
Entry point for running git-sensei as a module.

This allows the package to be run with: python -m git_sensei
"""

from .cli import app

if __name__ == "__main__":
    app()