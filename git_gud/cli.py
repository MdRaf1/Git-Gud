"""
CLI module for Git Gud.

This module provides the command-line interface and entry point for the application.
It handles argument parsing and coordinates between the safety and git_ops modules.
"""

from typing import Optional
import typer
import signal
import sys
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
    try:
        if execute is None:
            typer.echo("Error: No command provided", err=True)
            typer.echo("Usage: git-gud --execute '<git_command>'", err=True)
            typer.echo("Example: git-gud --execute 'git status'", err=True)
            raise typer.Exit(1)
        
        execute_command(execute)
        
    except KeyboardInterrupt:
        typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
        typer.echo("Exiting safely...", err=True)
        raise typer.Exit(130)
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        typer.echo(f"Error: Unexpected error occurred: {str(e)}", err=True)
        typer.echo("Please report this issue if it persists", err=True)
        raise typer.Exit(1)


def _handle_interrupt(signum, frame):
    """Handle Ctrl+C interruption gracefully."""
    typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
    typer.echo("Exiting safely...", err=True)
    sys.exit(130)  # Standard exit code for Ctrl+C


def execute_command(command: str) -> None:
    """
    Execute a Git command with safety checks.
    
    Args:
        command: The Git command string to execute
    """
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, _handle_interrupt)
    
    try:
        # Validate command input
        if not command or not command.strip():
            typer.echo("Error: Empty command provided", err=True)
            typer.echo("Please specify a Git command to execute", err=True)
            raise typer.Exit(1)
        
        # Check if Git is available
        if not is_git_available():
            typer.echo("Error: Git is not installed or not available in PATH", err=True)
            typer.echo("Please install Git and ensure it's accessible from the command line", err=True)
            typer.echo("Visit https://git-scm.com/downloads for installation instructions", err=True)
            raise typer.Exit(1)
        
        # Check command safety
        try:
            safety_check = check_command_safety(command)
        except Exception as e:
            typer.echo(f"Error: Failed to analyze command safety: {str(e)}", err=True)
            typer.echo("Command execution aborted for safety reasons", err=True)
            raise typer.Exit(1)
        
        if not safety_check.is_safe:
            # Display warning and get user confirmation
            typer.echo(f"WARNING: {safety_check.warning_message}", err=True)
            typer.echo(f"Dangerous patterns detected: {', '.join(safety_check.dangerous_patterns)}", err=True)
            
            try:
                if not get_user_confirmation(safety_check.warning_message):
                    typer.echo("Command execution aborted by user.", err=True)
                    return  # Exit normally when user rejects dangerous command
            except KeyboardInterrupt:
                typer.echo("\n\nOperation interrupted during confirmation.", err=True)
                typer.echo("Command execution aborted for safety.", err=True)
                raise typer.Exit(130)
            except Exception as e:
                typer.echo(f"Error during user confirmation: {str(e)}", err=True)
                typer.echo("Command execution aborted for safety reasons", err=True)
                raise typer.Exit(1)
        
        # Execute the Git command
        try:
            result = execute_git_command(command)
        except Exception as e:
            typer.echo(f"Error: Unexpected error during command execution: {str(e)}", err=True)
            typer.echo("Please check your Git installation and try again", err=True)
            raise typer.Exit(1)
        
        # Display results
        if result.success:
            if result.stdout:
                typer.echo(result.stdout)
        else:
            # Handle specific error cases with helpful messages
            if result.exit_code == 127:
                typer.echo("Error: Git command not found", err=True)
                typer.echo("Please ensure Git is properly installed and accessible", err=True)
            elif result.exit_code == 126:
                typer.echo("Error: Permission denied", err=True)
                typer.echo("Check your file permissions and repository access rights", err=True)
            elif result.exit_code == 124:
                typer.echo("Error: Command timed out", err=True)
                typer.echo("The Git operation took too long to complete", err=True)
            elif result.exit_code == 128:
                typer.echo("Error: Git repository error", err=True)
                if "not a git repository" in result.stderr.lower():
                    typer.echo("This directory is not a Git repository. Use 'git init' to initialize one.", err=True)
            else:
                typer.echo(f"Error: {result.stderr}", err=True)
            
            if result.stdout:
                typer.echo(result.stdout)
            
            typer.echo(f"Command failed with exit code: {result.exit_code}", err=True)
            raise typer.Exit(result.exit_code)
            
    except KeyboardInterrupt:
        typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
        typer.echo("Exiting safely...", err=True)
        raise typer.Exit(130)
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        typer.echo(f"Error: Unexpected error occurred: {str(e)}", err=True)
        typer.echo("Please report this issue if it persists", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()