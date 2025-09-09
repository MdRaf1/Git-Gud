"""
Safety module for Git Gud.

This module provides command validation and user confirmation for dangerous operations.
It analyzes Git commands for potentially destructive patterns and manages user consent.
"""

import re
from dataclasses import dataclass
from typing import List
import typer


@dataclass
class SafetyCheck:
    """
    Result of command safety analysis.
    
    Attributes:
        is_safe: Boolean indicating if command is safe to execute
        dangerous_patterns: List of dangerous patterns found in the command
        warning_message: Human-readable warning about the risks
    """
    is_safe: bool
    dangerous_patterns: List[str]
    warning_message: str


def load_dangerous_patterns() -> List[str]:
    """
    Load list of dangerous Git operation patterns.
    
    Returns:
        List of regex patterns that match dangerous Git operations
    """
    return [
        r"push\s+(-f|--force)",
        r"reset\s+--hard",
        r"filter-branch",
        r"rebase\s+(-i|--interactive)",
        r"checkout\s+(-f|--force)",
        r"clean\s+(-fd|-df|-f\s+-d|-d\s+-f)",
        r"reflog\s+expire",
        r"gc\s+--prune=now",
        r"update-ref\s+-d",
        r"branch\s+(-D|--delete\s+--force)",
        r"tag\s+(-d|--delete)",
        r"stash\s+(drop|clear)",
        r"worktree\s+(remove|prune)\s+--force",
    ]


def check_command_safety(command: str) -> SafetyCheck:
    """
    Analyze command for dangerous patterns.
    
    Args:
        command: Git command string to analyze
        
    Returns:
        SafetyCheck object with analysis results
    """
    dangerous_patterns = load_dangerous_patterns()
    found_patterns = []
    
    # Normalize command for pattern matching
    normalized_command = command.lower().strip()
    
    # Check each dangerous pattern
    for pattern in dangerous_patterns:
        if re.search(pattern, normalized_command):
            found_patterns.append(pattern)
    
    if found_patterns:
        warning_message = _generate_warning_message(found_patterns, command)
        return SafetyCheck(
            is_safe=False,
            dangerous_patterns=found_patterns,
            warning_message=warning_message
        )
    
    return SafetyCheck(
        is_safe=True,
        dangerous_patterns=[],
        warning_message=""
    )


def _generate_warning_message(patterns: List[str], command: str) -> str:
    """
    Generate appropriate warning message for detected dangerous operations.
    
    Args:
        patterns: List of dangerous patterns found
        command: Original command string
        
    Returns:
        Human-readable warning message
    """
    if any("push" in pattern and "force" in pattern for pattern in patterns):
        return "This command will force push changes, potentially overwriting remote history and causing data loss for other developers."
    
    if any("reset" in pattern and "hard" in pattern for pattern in patterns):
        return "This command will permanently discard uncommitted changes and reset your working directory."
    
    if any("filter-branch" in pattern for pattern in patterns):
        return "This command will rewrite Git history, which can cause serious issues for shared repositories."
    
    if any("clean" in pattern and "f" in pattern for pattern in patterns):
        return "This command will permanently delete untracked files and directories."
    
    if any("reflog" in pattern and "expire" in pattern for pattern in patterns):
        return "This command will remove reflog entries, making it harder to recover lost commits."
    
    if any("branch" in pattern and "D" in pattern for pattern in patterns):
        return "This command will force delete branches, potentially losing unmerged work."
    
    # Generic warning for other dangerous operations
    return f"This command contains potentially dangerous operations that could cause data loss or repository corruption."


def get_user_confirmation(warning_message: str) -> bool:
    """
    Prompt user for confirmation of dangerous operation.
    
    Args:
        warning_message: Warning message to display to user
        
    Returns:
        True if user confirms with "yes", False otherwise
    """
    typer.echo("\n" + "="*60)
    typer.echo("🚨 DANGEROUS OPERATION DETECTED 🚨")
    typer.echo("="*60)
    typer.echo(f"\n{warning_message}")
    typer.echo("\nThis operation could cause permanent data loss or repository corruption.")
    typer.echo("Please make sure you have backups and understand the consequences.")
    
    response = typer.prompt(
        "\nType 'yes' to proceed with this dangerous operation",
        type=str
    ).strip().lower()
    
    if response == "yes":
        typer.echo("Proceeding with dangerous operation...")
        return True
    else:
        typer.echo("Operation cancelled for safety.")
        return False