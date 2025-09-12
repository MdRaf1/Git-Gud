"""
Context module for Git sensei.

This module gathers repository context information to provide AI with
better understanding of the current Git state for smarter command generation.
"""

from .git_ops import execute_git_command


def get_git_context() -> str:
    """
    Gather repository context information for AI-powered command generation.

    Returns:
        A formatted string containing current repository state information
        including status, current branch, and recent commit history.
    """
    context_parts = []

    # Get current status
    try:
        status_result = execute_git_command("git status --porcelain")
        if status_result.success:
            if status_result.stdout.strip():
                context_parts.append(f"Status:\n{status_result.stdout.strip()}")
            else:
                context_parts.append("Status: Working directory clean")
        else:
            context_parts.append("Status: Unable to determine (not a git repository?)")
    except Exception:  # pylint: disable=broad-exception-caught
        context_parts.append("Status: Unable to determine")

    # Get current branch
    try:
        branch_result = execute_git_command("git branch --show-current")
        if branch_result.success and branch_result.stdout.strip():
            context_parts.append(f"Current branch: {branch_result.stdout.strip()}")
        else:
            # Fallback to get branch info from git status
            status_result = execute_git_command("git status")
            if status_result.success and "On branch" in status_result.stdout:
                for line in status_result.stdout.split("\n"):
                    if line.startswith("On branch"):
                        branch_name = line.replace("On branch ", "").strip()
                        context_parts.append(f"Current branch: {branch_name}")
                        break
            else:
                context_parts.append("Current branch: Unable to determine")
    except Exception:  # pylint: disable=broad-exception-caught
        context_parts.append("Current branch: Unable to determine")

    # Get recent commit history
    try:
        log_result = execute_git_command("git log --oneline -n 5")
        if log_result.success and log_result.stdout.strip():
            context_parts.append(f"Recent commits:\n{log_result.stdout.strip()}")
        else:
            context_parts.append("Recent commits: No commits found")
    except Exception:  # pylint: disable=broad-exception-caught
        context_parts.append("Recent commits: Unable to determine")

    # Combine all context information
    return "\n\n".join(context_parts)
