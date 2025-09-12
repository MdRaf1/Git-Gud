"""
CLI module for Git sensei.

This module provides the command-line interface and entry point for the application.
It handles argument parsing and coordinates between the safety and git_ops modules.
"""

import signal
import sys
from typing import List, Optional

import typer

from .ai import translate_to_git_sync
from .context import get_git_context
from .git_ops import execute_git_command, is_git_available
from .safety import check_command_safety, get_user_confirmation

app = typer.Typer(
    name="git-sensei",
    help="An AI-powered command-line assistant for safer Git usage",
    add_completion=False,
)


@app.command()
def main(
    execute: Optional[str] = typer.Option(
        None,
        "--execute",
        "-e",
        help="Git command to execute with safety checks",
    ),
    phrase: Optional[List[str]] = typer.Argument(
        None, help="Natural language description of what you want to do"
    ),
) -> None:
    """
    An AI-powered command-line assistant for safer Git usage.

    Execute Git commands with safety checks and user confirmation for dangerous
    operations. Use natural language to describe what you want to do, or use
    --execute for direct commands.
    """
    try:
        # If --execute flag is used, use Phase 1 workflow
        if execute is not None:
            execute_command(execute)
            return

        # If natural language arguments provided, use Phase 2 workflow
        if phrase:
            natural_language = " ".join(phrase)
            execute_natural_language(natural_language)
            return

        # No input provided at all
        typer.echo("Error: No command or phrase provided", err=True)
        typer.echo("Usage:", err=True)
        typer.echo(
            "  git-sensei --execute '<git_command>'  # Execute specific Git command",
            err=True,
        )
        typer.echo(
            "  git-sensei <natural_language>         # Translate natural language",
            err=True,
        )
        typer.echo("Examples:", err=True)
        typer.echo("  git-sensei --execute 'git status'", err=True)
        typer.echo("  git-sensei show me the last 5 commits", err=True)
        typer.echo("  git-sensei create a new branch called feature", err=True)
        raise typer.Exit(1)

    except KeyboardInterrupt as exc:
        typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
        typer.echo("Exiting safely...", err=True)
        raise typer.Exit(130) from exc
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:  # pylint: disable=broad-exception-caught
        typer.echo(f"Error: Unexpected error occurred: {str(e)}", err=True)
        typer.echo("Please report this issue if it persists", err=True)
        raise typer.Exit(1) from e


def _handle_interrupt(signum, frame):  # pylint: disable=unused-argument
    """Handle Ctrl+C interruption gracefully."""
    typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
    typer.echo("Exiting safely...", err=True)
    sys.exit(130)  # Standard exit code for Ctrl+C


def execute_natural_language(phrase: str) -> None:
    """
    Execute a natural language phrase by translating it to a Git command.

    Args:
        phrase: Natural language description of what the user wants to do
    """
    try:
        # Validate phrase input
        if not phrase or not phrase.strip():
            typer.echo("Error: Empty phrase provided", err=True)
            typer.echo("Please describe what you want to do with Git", err=True)
            raise typer.Exit(1)

        typer.echo(f"🤖 Translating: '{phrase}'")

        # Gather repository context for better AI decisions
        try:
            context = get_git_context()
            typer.echo("� Analyzing repository context...")
        except Exception as e:  # pylint: disable=broad-exception-caught
            typer.echo(f"⚠️  Warning: Could not gather repository context: {str(e)}")
            context = ""

        # Translate natural language to Git command with context
        try:
            git_command = translate_to_git_sync(phrase, context)
            typer.echo(f"💡 Suggested command: {git_command}")
        except ValueError as e:
            if "OPENROUTER_API_KEY" in str(e):
                typer.echo("Error: OpenRouter API key not found", err=True)
                typer.echo(
                    "Please set the OPENROUTER_API_KEY environment variable", err=True
                )
                typer.echo("Visit https://openrouter.ai to get your API key", err=True)
            else:
                typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error: Failed to translate phrase: {str(e)}", err=True)
            typer.echo(
                "Please try rephrasing your request or use --execute with a "
                "direct Git command",
                err=True,
            )
            raise typer.Exit(1)

        # Execute the translated command using existing workflow
        execute_command(git_command)

    except KeyboardInterrupt as exc:
        typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
        typer.echo("Exiting safely...", err=True)
        raise typer.Exit(130) from exc
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        typer.echo(f"Error: Unexpected error occurred: {str(e)}", err=True)
        typer.echo("Please report this issue if it persists", err=True)
        raise typer.Exit(1)


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
            typer.echo(
                "Please install Git and ensure it's accessible from the command line",
                err=True,
            )
            typer.echo(
                "Visit https://git-scm.com/downloads for installation instructions",
                err=True,
            )
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
            patterns = ", ".join(safety_check.dangerous_patterns)
            typer.echo(f"Dangerous patterns detected: {patterns}", err=True)

            try:
                if not get_user_confirmation(safety_check.warning_message):
                    typer.echo("Command execution aborted by user.", err=True)
                    return  # Exit normally when user rejects dangerous command
            except KeyboardInterrupt as exc:
                typer.echo("\n\nOperation interrupted during confirmation.", err=True)
                typer.echo("Command execution aborted for safety.", err=True)
                raise typer.Exit(130) from exc
            except Exception as e:
                typer.echo(f"Error during user confirmation: {str(e)}", err=True)
                typer.echo("Command execution aborted for safety reasons", err=True)
                raise typer.Exit(1)

        # Execute the Git command
        try:
            result = execute_git_command(command)
        except Exception as e:
            typer.echo(
                f"Error: Unexpected error during command execution: {str(e)}", err=True
            )
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
                typer.echo(
                    "Please ensure Git is properly installed and accessible", err=True
                )
            elif result.exit_code == 126:
                typer.echo("Error: Permission denied", err=True)
                typer.echo(
                    "Check your file permissions and repository access rights", err=True
                )
            elif result.exit_code == 124:
                typer.echo("Error: Command timed out", err=True)
                typer.echo("The Git operation took too long to complete", err=True)
            elif result.exit_code == 128:
                typer.echo("Error: Git repository error", err=True)
                if "not a git repository" in result.stderr.lower():
                    typer.echo(
                        "This directory is not a Git repository. "
                        "Use 'git init' to initialize one.",
                        err=True,
                    )
            else:
                typer.echo(f"Error: {result.stderr}", err=True)

            if result.stdout:
                typer.echo(result.stdout)

            typer.echo(f"Command failed with exit code: {result.exit_code}", err=True)
            raise typer.Exit(result.exit_code)

    except KeyboardInterrupt as exc:
        typer.echo("\n\nOperation interrupted by user (Ctrl+C).", err=True)
        typer.echo("Exiting safely...", err=True)
        raise typer.Exit(130) from exc
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        typer.echo(f"Error: Unexpected error occurred: {str(e)}", err=True)
        typer.echo("Please report this issue if it persists", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
