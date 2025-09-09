"""
CLI module for Git Gud.

This module provides the command-line interface and entry point for the application.
It handles argument parsing and coordinates between the safety and git_ops modules.
"""

from typing import Optional
import typer
from .git_ops import execute_git_command, is_git_available
from .safety import check_command_safety, get_user_confirmation

app = typer.Typer(
    name="git-gud",
    help="An AI-powered command-line assistant for safer Git usage",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main(
    execute: Optional[str] = typer.Option(
        None,
        "--execute",
        "-e",
        help="Git command to execute with safety checks",
    )
) -> None:
    """
    An AI-powered command-line assistant for safer Git usage.
    
    Execute Git commands with safety checks and user confirmation for dangerous operations.
    """
    if execute is None:
        typer.echo("Error: No command provided", err=True)
        typer.echo("Usage: git-gud --execute '<git_command>'", err=True)
        typer.echo("Example: git-gud --execute 'git status'", err=True)
        raise typer.Exit(1)
    
    execute_command(execute)


def execute_command(command: str) -> None:
    """
    Execute a Git command with safety checks.
    
    Args:
        command: The Git command string to execute
    """
    # Check if Git is available
    if not is_git_available():
        typer.echo("Error: Git is not installed or not available in PATH", err=True)
        typer.echo("Please install Git and ensure it's accessible from the command line", err=True)
        raise typer.Exit(1)
    
    # Check command safety
    safety_check = check_command_safety(command)
    
    if not safety_check.is_safe:
        # Display warning and get user confirmation
        typer.echo(f"⚠️  WARNING: {safety_check.warning_message}", err=True)
        typer.echo(f"Dangerous patterns detected: {', '.join(safety_check.dangerous_patterns)}", err=True)
        
        if not get_user_confirmation(safety_check.warning_message):
            typer.echo("Command execution aborted by user.", err=True)
            raise typer.Exit(0)
    
    # Execute the Git command
    result = execute_git_command(command)
    
    # Display results
    if result.success:
        if result.stdout:
            typer.echo(result.stdout)
    else:
        if result.stderr:
            typer.echo(f"Error: {result.stderr}", err=True)
        if result.stdout:
            typer.echo(result.stdout)
        typer.echo(f"Command failed with exit code: {result.exit_code}", err=True)
        raise typer.Exit(result.exit_code)


if __name__ == "__main__":
    app()