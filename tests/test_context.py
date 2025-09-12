"""
Tests for the context module.
"""

from unittest.mock import patch

from git_sensei.context import get_git_context
from git_sensei.git_ops import GitResult


class TestGetGitContext:
    """Test cases for get_git_context function."""

    @patch("git_sensei.context.execute_git_command")
    def test_get_git_context_success(self, mock_execute):
        """Test successful context gathering."""
        # Mock successful git command results
        mock_results = [
            GitResult(
                success=True,
                stdout="M  file1.py\nA  file2.py",
                stderr="",
                exit_code=0,
                command="git status --porcelain",
            ),
            GitResult(
                success=True,
                stdout="main",
                stderr="",
                exit_code=0,
                command="git branch --show-current",
            ),
            GitResult(
                success=True,
                stdout="abc123 Latest commit\ndef456 Previous commit",
                stderr="",
                exit_code=0,
                command="git log --oneline -n 5",
            ),
        ]
        mock_execute.side_effect = mock_results

        context = get_git_context()

        assert "Status:" in context
        assert "M  file1.py" in context
        assert "Current branch: main" in context
        assert "Recent commits:" in context
        assert "abc123 Latest commit" in context

    @patch("git_sensei.context.execute_git_command")
    def test_get_git_context_clean_status(self, mock_execute):
        """Test context gathering with clean working directory."""
        mock_results = [
            GitResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
                command="git status --porcelain",
            ),
            GitResult(
                success=True,
                stdout="main",
                stderr="",
                exit_code=0,
                command="git branch --show-current",
            ),
            GitResult(
                success=True,
                stdout="abc123 Latest commit",
                stderr="",
                exit_code=0,
                command="git log --oneline -n 5",
            ),
        ]
        mock_execute.side_effect = mock_results

        context = get_git_context()

        assert "Status: Working directory clean" in context
        assert "Current branch: main" in context
        assert "Recent commits:" in context

    @patch("git_sensei.context.execute_git_command")
    def test_get_git_context_git_failures(self, mock_execute):
        """Test context gathering when git commands fail."""
        mock_results = [
            GitResult(
                success=False,
                stdout="",
                stderr="not a git repository",
                exit_code=128,
                command="git status --porcelain",
            ),
            GitResult(
                success=False,
                stdout="",
                stderr="not a git repository",
                exit_code=128,
                command="git branch --show-current",
            ),
            GitResult(
                success=False,
                stdout="",
                stderr="not a git repository",
                exit_code=128,
                command="git log --oneline -n 5",
            ),
        ]
        mock_execute.side_effect = mock_results

        context = get_git_context()

        assert "Status: Unable to determine" in context
        assert "Current branch: Unable to determine" in context
        assert "Recent commits: Unable to determine" in context

    @patch("git_sensei.context.execute_git_command")
    def test_get_git_context_branch_fallback(self, mock_execute):
        """Test branch detection fallback to git status."""

        def mock_execute_side_effect(command):
            if "git status --porcelain" in command:
                return GitResult(
                    success=True, stdout="", stderr="", exit_code=0, command=command
                )
            elif "git branch --show-current" in command:
                return GitResult(
                    success=True, stdout="", stderr="", exit_code=0, command=command
                )
            elif "git status" in command:
                return GitResult(
                    success=True,
                    stdout="On branch feature-branch\nnothing to commit",
                    stderr="",
                    exit_code=0,
                    command=command,
                )
            elif "git log" in command:
                return GitResult(
                    success=True,
                    stdout="abc123 Latest commit",
                    stderr="",
                    exit_code=0,
                    command=command,
                )
            return GitResult(
                success=False, stdout="", stderr="", exit_code=1, command=command
            )

        mock_execute.side_effect = mock_execute_side_effect

        context = get_git_context()

        assert "Current branch: feature-branch" in context

    @patch("git_sensei.context.execute_git_command")
    def test_get_git_context_exceptions(self, mock_execute):
        """Test context gathering when exceptions occur."""
        mock_execute.side_effect = Exception("Git command failed")

        context = get_git_context()

        assert "Status: Unable to determine" in context
        assert "Current branch: Unable to determine" in context
        assert "Recent commits: Unable to determine" in context
