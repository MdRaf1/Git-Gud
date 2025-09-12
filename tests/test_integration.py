"""
Integration tests for Git sensei end-to-end workflows.

Tests complete workflows from CLI input to final output, including
safe command execution, dangerous command confirmation, and error handling.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from git_sensei.cli import app


class TestSafeCommandWorkflows:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for safe command execution workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_git_status_complete_workflow(self, mock_execute, mock_git_available):
        """Test complete workflow for git status command."""
        # Setup mocks for successful git status
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="On branch main\nnothing to commit, working tree clean",
            stderr="",
            exit_code=0,
            command="git status",
            success=True,
        )

        # Execute through CLI
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "On branch main" in result.stdout
        assert "nothing to commit" in result.stdout

        # Verify all components were called
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git status")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_git_log_complete_workflow(self, mock_execute, mock_git_available):
        """Test complete workflow for git log command."""
        # Setup mocks for git log
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="commit abc123\nAuthor: Test User\nDate: Mon Jan 1 12:00:00 2024\n\n    Initial commit",
            stderr="",
            exit_code=0,
            command="git log --oneline -n 1",
            success=True,
        )

        # Execute through CLI
        result = self.runner.invoke(app, ["--execute", "git log --oneline -n 1"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "commit abc123" in result.stdout
        assert "Initial commit" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git log --oneline -n 1")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_git_diff_complete_workflow(self, mock_execute, mock_git_available):
        """Test complete workflow for git diff command."""
        # Setup mocks for git diff
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="diff --git a/file.txt b/file.txt\nindex 1234567..abcdefg 100644\n--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-old content\n+new content",
            stderr="",
            exit_code=0,
            command="git diff",
            success=True,
        )

        # Execute through CLI
        result = self.runner.invoke(app, ["--execute", "git diff"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "diff --git" in result.stdout
        assert "old content" in result.stdout
        assert "new content" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git diff")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_git_branch_complete_workflow(self, mock_execute, mock_git_available):
        """Test complete workflow for git branch command."""
        # Setup mocks for git branch
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="* main\n  feature-branch\n  develop",
            stderr="",
            exit_code=0,
            command="git branch",
            success=True,
        )

        # Execute through CLI
        result = self.runner.invoke(app, ["--execute", "git branch"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "* main" in result.stdout
        assert "feature-branch" in result.stdout
        assert "develop" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git branch")


class TestDangerousCommandWorkflows:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for dangerous command workflows with confirmation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    @patch("git_sensei.cli.execute_git_command")
    def test_force_push_confirmed_workflow(
        self, mock_execute, mock_confirm, mock_git_available
    ):
        """Test complete workflow for confirmed force push."""
        # Setup mocks for dangerous command confirmation
        mock_git_available.return_value = True
        mock_confirm.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="Everything up-to-date",
            stderr="",
            exit_code=0,
            command="git push --force origin main",
            success=True,
        )

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git push --force origin main"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "Everything up-to-date" in result.stdout

        # Verify all workflow steps
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()
        mock_execute.assert_called_once_with("git push --force origin main")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    def test_force_push_rejected_workflow(self, mock_confirm, mock_git_available):
        """Test complete workflow for rejected force push."""
        # Setup mocks for dangerous command rejection
        mock_git_available.return_value = True
        mock_confirm.return_value = False

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git push --force origin main"])

        # Verify workflow stops at confirmation
        assert result.exit_code == 0
        output = result.stdout + result.stderr
        assert "Command execution aborted by user" in output

        # Verify workflow steps up to confirmation
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    @patch("git_sensei.cli.execute_git_command")
    def test_reset_hard_confirmed_workflow(
        self, mock_execute, mock_confirm, mock_git_available
    ):
        """Test complete workflow for confirmed reset hard."""
        # Setup mocks for dangerous reset command
        mock_git_available.return_value = True
        mock_confirm.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="HEAD is now at abc1234 Initial commit",
            stderr="",
            exit_code=0,
            command="git reset --hard HEAD~1",
            success=True,
        )

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git reset --hard HEAD~1"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "HEAD is now at abc1234" in result.stdout

        # Verify all workflow steps
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()
        mock_execute.assert_called_once_with("git reset --hard HEAD~1")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    def test_reset_hard_rejected_workflow(self, mock_confirm, mock_git_available):
        """Test complete workflow for rejected reset hard."""
        # Setup mocks for dangerous command rejection
        mock_git_available.return_value = True
        mock_confirm.return_value = False

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git reset --hard HEAD~1"])

        # Verify workflow stops at confirmation
        assert result.exit_code == 0
        output = result.stdout + result.stderr
        assert "Command execution aborted by user" in output

        # Verify workflow steps up to confirmation
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    @patch("git_sensei.cli.execute_git_command")
    def test_clean_force_confirmed_workflow(
        self, mock_execute, mock_confirm, mock_git_available
    ):
        """Test complete workflow for confirmed clean force."""
        # Setup mocks for dangerous clean command
        mock_git_available.return_value = True
        mock_confirm.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="Removing untracked_file.txt\nRemoving temp_dir/",
            stderr="",
            exit_code=0,
            command="git clean -fd",
            success=True,
        )

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git clean -fd"])

        # Verify complete workflow
        assert result.exit_code == 0
        assert "Removing untracked_file.txt" in result.stdout
        assert "Removing temp_dir/" in result.stdout

        # Verify all workflow steps
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()
        mock_execute.assert_called_once_with("git clean -fd")


class TestErrorHandlingWorkflows:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for error handling across module boundaries."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_git_not_available_workflow(self):
        """Test complete workflow when Git is not available."""
        # Use real is_git_available but mock it to return False
        with patch("git_sensei.cli.is_git_available", return_value=False):
            result = self.runner.invoke(app, ["--execute", "git status"])

            # Verify workflow stops at Git check
            assert result.exit_code == 1
            output = result.stdout + result.stderr
            assert "Error: Git is not installed" in output
            assert "Please install Git" in output

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_git_repository_error_workflow(self, mock_execute, mock_git_available):
        """Test workflow with Git repository error."""
        # Setup mocks for repository error
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="",
            stderr="fatal: not a git repository (or any of the parent directories): .git",
            exit_code=128,
            command="git status",
            success=False,
        )

        # Execute command that will fail
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify error handling workflow
        assert result.exit_code == 128
        output = result.stdout + result.stderr
        assert "Git repository error" in output
        assert "not a Git repository" in output
        assert "git init" in output

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git status")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_permission_denied_error_workflow(self, mock_execute, mock_git_available):
        """Test workflow with permission denied error."""
        # Setup mocks for permission error
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="",
            stderr="Permission denied",
            exit_code=126,
            command="git status",
            success=False,
        )

        # Execute command that will fail
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify error handling workflow
        assert result.exit_code == 126
        output = result.stdout + result.stderr
        assert "Permission denied" in output
        assert "Check your file permissions" in output

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git status")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_command_timeout_error_workflow(self, mock_execute, mock_git_available):
        """Test workflow with command timeout error."""
        # Setup mocks for timeout error
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="",
            stderr="Command timed out after 30 seconds",
            exit_code=124,
            command="git status",
            success=False,
        )

        # Execute command that will timeout
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify error handling workflow
        assert result.exit_code == 124
        output = result.stdout + result.stderr
        assert "Command timed out" in output
        assert "took too long to complete" in output

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git status")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.check_command_safety")
    def test_safety_check_error_workflow(self, mock_safety, mock_git_available):
        """Test workflow when safety check fails."""
        # Setup mocks for safety check failure
        mock_git_available.return_value = True
        mock_safety.side_effect = Exception("Safety check failed")

        # Execute command when safety check fails
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify error handling workflow
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Failed to analyze command safety" in output
        assert "Command execution aborted for safety reasons" in output

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git status")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    def test_confirmation_error_workflow(self, mock_confirm, mock_git_available):
        """Test workflow when user confirmation fails."""
        # Setup mocks for confirmation failure
        mock_git_available.return_value = True
        mock_confirm.side_effect = Exception("Confirmation failed")

        # Execute dangerous command when confirmation fails
        result = self.runner.invoke(app, ["--execute", "git push --force"])

        # Verify error handling workflow
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Error during user confirmation" in output
        assert "Command execution aborted for safety reasons" in output

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()

    def test_empty_command_workflow(self):
        """Test workflow with empty command."""
        result = self.runner.invoke(app, ["--execute", ""])

        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Empty command provided" in output

    def test_no_command_provided_workflow(self):
        """Test workflow when no command is provided."""
        result = self.runner.invoke(app, [])

        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Error: No command or phrase provided" in output
        assert "git-sensei --execute '<git_command>'" in output


class TestKeyboardInterruptWorkflows:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for keyboard interrupt handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    def test_keyboard_interrupt_during_confirmation_workflow(
        self, mock_confirm, mock_git_available
    ):
        """Test workflow when user interrupts during confirmation."""
        # Setup mocks for keyboard interrupt during confirmation
        mock_git_available.return_value = True
        mock_confirm.side_effect = KeyboardInterrupt()

        # Execute dangerous command and interrupt during confirmation
        result = self.runner.invoke(app, ["--execute", "git push --force"])

        # Verify interrupt handling workflow
        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "interrupted during confirmation" in output

        # Verify workflow execution up to interrupt
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()

    @patch("git_sensei.cli.execute_command")
    def test_keyboard_interrupt_main_workflow(self, mock_execute):
        """Test workflow when user interrupts main execution."""
        # Setup mock for keyboard interrupt in main
        mock_execute.side_effect = KeyboardInterrupt()

        # Execute command and interrupt
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify interrupt handling workflow
        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "interrupted by user" in output


class TestRealGitIntegration:  # pylint: disable=attribute-defined-outside-init
    """Integration tests using real Git repositories (when available)."""

    def setup_method(self):
        """Set up test fixtures with temporary Git repository."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Initialize a real Git repository for testing
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                check=True,
                capture_output=True,
            )

            # Create a test file and commit
            test_file = Path("test.txt")
            test_file.write_text("Initial content", encoding="utf-8")
            subprocess.run(["git", "add", "test.txt"], check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                check=True,
                capture_output=True,
            )

            self.git_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.git_available = False

    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        # Clean up temp directory

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.skipif(
        not hasattr(subprocess, "run"), reason="subprocess.run not available"
    )
    def test_real_git_status_workflow(self):
        """Test workflow with real Git repository for status command."""
        if not self.git_available:
            pytest.skip("Git not available or repository setup failed")

        # Execute real git status through our CLI
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify successful execution
        assert result.exit_code == 0
        # Should contain typical git status output
        assert (
            "On branch" in result.stdout
            or "working tree clean" in result.stdout
            or "nothing to commit" in result.stdout
        )

    @pytest.mark.skipif(
        not hasattr(subprocess, "run"), reason="subprocess.run not available"
    )
    def test_real_git_log_workflow(self):
        """Test workflow with real Git repository for log command."""
        if not self.git_available:
            pytest.skip("Git not available or repository setup failed")

        # Execute real git log through our CLI
        result = self.runner.invoke(app, ["--execute", "git log --oneline -n 1"])

        # Verify successful execution
        assert result.exit_code == 0
        # Should contain commit hash and message
        assert "Initial commit" in result.stdout

    @pytest.mark.skipif(
        not hasattr(subprocess, "run"), reason="subprocess.run not available"
    )
    def test_real_git_branch_workflow(self):
        """Test workflow with real Git repository for branch command."""
        if not self.git_available:
            pytest.skip("Git not available or repository setup failed")

        # Execute real git branch through our CLI
        result = self.runner.invoke(app, ["--execute", "git branch"])

        # Verify successful execution
        assert result.exit_code == 0
        # Should show current branch (main or master)
        assert "main" in result.stdout or "master" in result.stdout

    @pytest.mark.skipif(
        not hasattr(subprocess, "run"), reason="subprocess.run not available"
    )
    def test_real_git_repository_error_workflow(self):
        """Test workflow with real Git error (outside repository)."""
        if not self.git_available:
            pytest.skip("Git not available")

        # Change to a non-Git directory
        non_git_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        try:
            os.chdir(non_git_dir)

            # Execute git status in non-Git directory
            result = self.runner.invoke(app, ["--execute", "git status"])

            # Verify error handling
            assert result.exit_code == 128
            output = result.stdout + result.stderr
            assert "Git repository error" in output

        finally:
            os.chdir(original_cwd)

            shutil.rmtree(non_git_dir, ignore_errors=True)


class TestComplexWorkflows:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for complex command workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_complex_safe_command_workflow(self, mock_execute, mock_git_available):
        """Test workflow with complex safe command."""
        # Setup mocks for complex git command
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="commit abc123 (HEAD -> main, origin/main)\nAuthor: Test User <test@example.com>\nDate: Mon Jan 1 12:00:00 2024 +0000\n\n    Add new feature\n\n    - Implemented user authentication\n    - Added input validation\n    - Updated documentation",
            stderr="",
            exit_code=0,
            command="git log --graph --pretty=format:'%h (%d) %an <%ae> %ad %n%n    %s%n%n%b' --date=rfc -n 1",
            success=True,
        )

        # Execute complex command through CLI
        result = self.runner.invoke(
            app,
            [
                "--execute",
                "git log --graph --pretty=format:'%h (%d) %an <%ae> %ad %n%n    %s%n%n%b' --date=rfc -n 1",
            ],
        )

        # Verify complete workflow
        assert result.exit_code == 0
        assert "commit abc123" in result.stdout
        assert "Add new feature" in result.stdout
        assert "Implemented user authentication" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_command_with_mixed_output_workflow(self, mock_execute, mock_git_available):
        """Test workflow with command that has both stdout and stderr."""
        # Setup mocks for command with mixed output
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="On branch main\nYour branch is up to date with 'origin/main'.\n\nnothing to commit, working tree clean",
            stderr="warning: LF will be replaced by CRLF in file.txt",
            exit_code=0,
            command="git status",
            success=True,
        )

        # Execute command with mixed output
        result = self.runner.invoke(app, ["--execute", "git status"])

        # Verify workflow handles mixed output correctly
        assert result.exit_code == 0
        assert "On branch main" in result.stdout
        assert "nothing to commit" in result.stdout
        # Note: stderr warnings are not displayed for successful commands in current implementation

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git status")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.get_user_confirmation")
    @patch("git_sensei.cli.execute_git_command")
    def test_multiple_dangerous_patterns_workflow(
        self, mock_execute, mock_confirm, mock_git_available
    ):
        """Test workflow with command containing multiple dangerous patterns."""
        # Setup mocks for command with multiple dangerous patterns
        mock_git_available.return_value = True
        mock_confirm.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="HEAD is now at abc1234 Initial commit\nEverything up-to-date",
            stderr="",
            exit_code=0,
            command="git reset --hard HEAD~1 && git push --force",
            success=True,
        )

        # Execute command with multiple dangerous patterns
        result = self.runner.invoke(
            app, ["--execute", "git reset --hard HEAD~1 && git push --force"]
        )

        # Verify workflow handles multiple dangerous patterns
        assert result.exit_code == 0
        assert "HEAD is now at abc1234" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_confirm.assert_called_once()
        mock_execute.assert_called_once()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_command_with_special_characters_workflow(
        self, mock_execute, mock_git_available
    ):
        """Test workflow with command containing special characters."""
        # Setup mocks for command with special characters
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="commit abc123\nAuthor: Test User <test@example.com>\nDate: Mon Jan 1 12:00:00 2024\n\n    Fix: Handle special chars in commit message (issue #123)\n\n    - Added support for unicode characters: éñ中文\n    - Fixed parsing of commit messages with quotes and symbols\n    - Updated regex patterns to handle edge cases",
            stderr="",
            exit_code=0,
            command="git log --grep='Fix:.*#[0-9]+' --oneline -n 1",
            success=True,
        )

        # Execute command with special characters
        result = self.runner.invoke(
            app, ["--execute", "git log --grep='Fix:.*#[0-9]+' --oneline -n 1"]
        )

        # Verify workflow handles special characters
        assert result.exit_code == 0
        assert "Fix: Handle special chars" in result.stdout
        assert "éñ中文" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once()


class TestWorkflowPerformance:  # pylint: disable=attribute-defined-outside-init
    """Integration tests for workflow performance and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_large_output_workflow(self, mock_execute, mock_git_available):
        """Test workflow with large command output."""
        # Setup mocks for command with large output
        large_output = "\n".join(
            [
                f"commit {i:040x}\nAuthor: Test User <test@example.com>\nDate: Mon Jan {i+1} 12:00:00 2024\n\n    Commit message {i}\n"
                for i in range(100)
            ]
        )

        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout=large_output,
            stderr="",
            exit_code=0,
            command="git log --oneline -n 100",
            success=True,
        )

        # Execute command with large output
        result = self.runner.invoke(app, ["--execute", "git log --oneline -n 100"])

        # Verify workflow handles large output
        assert result.exit_code == 0
        assert "Commit message 0" in result.stdout
        assert "Commit message 99" in result.stdout

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git log --oneline -n 100")

    @patch("git_sensei.cli.is_git_available")
    @patch("git_sensei.cli.execute_git_command")
    def test_empty_output_workflow(self, mock_execute, mock_git_available):
        """Test workflow with empty command output."""
        # Setup mocks for command with empty output
        mock_git_available.return_value = True
        mock_execute.return_value = MagicMock(
            stdout="", stderr="", exit_code=0, command="git diff", success=True
        )

        # Execute command with empty output
        result = self.runner.invoke(app, ["--execute", "git diff"])

        # Verify workflow handles empty output
        assert result.exit_code == 0
        # Should not crash with empty output

        # Verify workflow execution
        mock_git_available.assert_called_once()
        mock_execute.assert_called_once_with("git diff")

    def test_rapid_successive_commands_workflow(self):
        """Test workflow with rapid successive command executions."""
        with patch("git_sensei.cli.is_git_available", return_value=True), patch(
            "git_sensei.cli.execute_git_command"
        ) as mock_execute:

            # Setup mock for rapid commands
            mock_execute.return_value = MagicMock(
                stdout="test output", stderr="", exit_code=0, success=True
            )

            # Execute multiple commands rapidly
            commands = ["git status", "git branch", "git log --oneline -n 1"]
            results = []

            for cmd in commands:
                mock_execute.return_value.command = cmd
                result = self.runner.invoke(app, ["--execute", cmd])
                results.append(result)

            # Verify all commands executed successfully
            for result in results:
                assert result.exit_code == 0
                assert "test output" in result.stdout

            # Verify all commands were executed
            assert mock_execute.call_count == len(commands)
