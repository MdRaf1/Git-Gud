"""
Git interaction module for Git Gud.

This module provides an abstraction layer for Git command execution,
handling subprocess calls and returning structured results.
"""

import subprocess
import shutil
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GitResult:
    """
    Structured result from Git command execution.
    
    Attributes:
        stdout: Standard output from the command
        stderr: Standard error output  
        exit_code: Process exit code
        command: Original command that was executed
        success: Boolean indicating if command succeeded (exit_code == 0)
    """
    stdout: str
    stderr: str
    exit_code: int
    command: str
    success: bool


def is_git_available() -> bool:
    """
    Check if Git is installed and accessible.
    
    Returns:
        True if Git is available, False otherwise
    """
    return shutil.which("git") is not None


def get_git_version() -> Optional[str]:
    """
    Get installed Git version.
    
    Returns:
        Git version string if available, None if Git is not installed
    """
    if not is_git_available():
        return None
    
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    return None


def execute_git_command(command: str, timeout: int = 30) -> GitResult:
    """
    Execute Git command and return structured result.
    
    Args:
        command: Git command string to execute
        timeout: Maximum time to wait for command completion in seconds
        
    Returns:
        GitResult object with execution details
        
    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
    """
    # Parse command string into list for subprocess
    # Remove 'git' prefix if present since we'll add it
    cmd_parts = command.strip().split()
    if cmd_parts and cmd_parts[0].lower() == "git":
        cmd_parts = cmd_parts[1:]
    
    # Construct full command
    full_command = ["git"] + cmd_parts
    
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )
        
        return GitResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            command=command,
            success=result.returncode == 0
        )
        
    except subprocess.TimeoutExpired as e:
        return GitResult(
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=124,  # Standard timeout exit code
            command=command,
            success=False
        )
    except subprocess.SubprocessError as e:
        return GitResult(
            stdout="",
            stderr=f"Subprocess error: {str(e)}",
            exit_code=1,
            command=command,
            success=False
        )