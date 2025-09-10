"""
Unit tests for the CLI module.

Tests the command-line interface, argument parsing, and command execution workflow.
"""

import pytest
from unittest.mock import Mock, patch, call
from typer.testing import CliRunner
from git_gud.cli import app, execute_command
from git_gud.git_ops import GitResult
from git_gud.safety import SafetyCheck


class TestCLI:
    """Test cases for CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help_message(self):
        """Test that CLI shows help when no arguments provided."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "An AI-powered command-line assistant for safer Git usage" in result.stdout

    def test_execute_command_help(self):
        """Test that execute command shows help."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "--execute" in result.stdout
        assert "Git command to execute with safety checks" in result.stdout

    def test_execute_command_no_arguments(self):
        """Test that execute command shows error when no command provided."""
        result = self.runner.invoke(app, [])
        assert result.exit_code == 1
        # Error messages go to stderr, but typer.testing captures them in stdout
        output = result.stdout + result.stderr
        assert "Error: No command or phrase provided" in output
        assert "git-gud --execute '<git_command>'" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_safe_command_success(self, mock_execute, mock_safety, mock_git_available):
        """Test executing a safe command successfully."""
        # Setup mocks
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="On branch main\nnothing to commit, working tree clean",
            stderr="",
            exit_code=0,
            command="git status",
            success=True
        )

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 0
        assert "On branch main" in result.stdout
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git status")
        mock_execute.assert_called_once_with("git status")

    @patch('git_gud.cli.is_git_available')
    def test_execute_command_git_not_available(self, mock_git_available):
        """Test error when Git is not available."""
        mock_git_available.return_value = False

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 1
        # Error messages go to stderr, but typer.testing captures them in stdout
        output = result.stdout + result.stderr
        assert "Error: Git is not installed" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_dangerous_command_confirmed(self, mock_execute, mock_confirm, mock_safety, mock_git_available):
        """Test executing a dangerous command with user confirmation."""
        # Setup mocks
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["--force"],
            warning_message="This command will force push and may overwrite remote changes"
        )
        mock_confirm.return_value = True
        mock_execute.return_value = GitResult(
            stdout="Everything up-to-date",
            stderr="",
            exit_code=0,
            command="git push --force origin main",
            success=True
        )

        result = self.runner.invoke(app, ["--execute", "git push --force origin main"])
        
        assert result.exit_code == 0
        assert "Everything up-to-date" in result.stdout
        mock_confirm.assert_called_once()

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    def test_execute_dangerous_command_rejected(self, mock_confirm, mock_safety, mock_git_available):
        """Test rejecting a dangerous command."""
        # Setup mocks
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["--force"],
            warning_message="This command will force push and may overwrite remote changes"
        )
        mock_confirm.return_value = False

        result = self.runner.invoke(app, ["--execute", "git push --force origin main"])
        
        assert result.exit_code == 0
        # Error messages go to stderr, but typer.testing captures them in stdout
        output = result.stdout + result.stderr
        assert "Command execution aborted by user" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_command_failure(self, mock_execute, mock_safety, mock_git_available):
        """Test handling of failed Git command."""
        # Setup mocks
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="",
            stderr="fatal: not a git repository",
            exit_code=128,
            command="git status",
            success=False
        )

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 128
        # Error messages go to stderr, but typer.testing captures them in stdout
        output = result.stdout + result.stderr
        assert "Git repository error" in output
        assert "Command failed with exit code: 128" in output


class TestExecuteCommandFunction:
    """Test cases for the execute_command function directly."""

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    @patch('typer.echo')
    def test_execute_command_safe_success(self, mock_echo, mock_execute, mock_safety, mock_git_available):
        """Test execute_command function with safe command."""
        # Setup mocks
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="branch info",
            stderr="",
            exit_code=0,
            command="git branch",
            success=True
        )

        execute_command("git branch")

        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git branch")
        mock_execute.assert_called_once_with("git branch")
        mock_echo.assert_called_once_with("branch info")

    @patch('git_gud.cli.is_git_available')
    @patch('typer.echo')
    def test_execute_command_git_unavailable(self, mock_echo, mock_git_available):
        """Test execute_command when Git is not available."""
        mock_git_available.return_value = False

        # typer.Exit raises click.exceptions.Exit, not SystemExit
        from click.exceptions import Exit
        with pytest.raises(Exit) as exc_info:
            execute_command("git status")

        assert exc_info.value.exit_code == 1
        # Check that error messages were displayed
        assert mock_echo.call_count >= 2
        error_calls = [call[0][0] for call in mock_echo.call_args_list]
        assert any("Git is not installed" in msg for msg in error_calls)

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    @patch('typer.echo')
    def test_execute_command_dangerous_rejected(self, mock_echo, mock_confirm, mock_safety, mock_git_available):
        """Test execute_command with dangerous command that's rejected."""
        # Setup mocks
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["reset --hard"],
            warning_message="This will permanently delete uncommitted changes"
        )
        mock_confirm.return_value = False

        # The function should return normally (no exception) when user rejects
        execute_command("git reset --hard HEAD~1")
        
        # Verify warning was shown and confirmation was called
        warning_calls = [call for call in mock_echo.call_args_list if call[1].get('err')]
        assert len(warning_calls) >= 2  # Warning message and patterns
        assert any("WARNING" in str(call) for call in warning_calls)
        # Verify warning was shown
        warning_calls = [call for call in mock_echo.call_args_list if call[1].get('err')]
        assert len(warning_calls) >= 2  # Warning message and patterns
        assert any("WARNING" in str(call) for call in warning_calls)

class TestIntegrationWorkflows:
    """Integration tests for complete command execution workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_complete_safe_command_workflow(self, mock_execute, mock_safety, mock_git_available):
        """Test complete workflow for safe command from CLI to output."""
        # Setup mocks for safe command workflow
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="* main\n  feature-branch\n  develop",
            stderr="",
            exit_code=0,
            command="git branch",
            success=True
        )

        # Execute command through CLI
        result = self.runner.invoke(app, ["--execute", "git branch"])
        
        # Verify complete workflow
        assert result.exit_code == 0
        assert "* main" in result.stdout
        assert "feature-branch" in result.stdout
        
        # Verify all workflow steps were called
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git branch")
        mock_execute.assert_called_once_with("git branch")

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    @patch('git_gud.cli.execute_git_command')
    def test_complete_dangerous_command_workflow_confirmed(self, mock_execute, mock_confirm, mock_safety, mock_git_available):
        """Test complete workflow for dangerous command with confirmation."""
        # Setup mocks for dangerous command workflow
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["--hard"],
            warning_message="This will permanently delete uncommitted changes"
        )
        mock_confirm.return_value = True
        mock_execute.return_value = GitResult(
            stdout="HEAD is now at abc1234 Initial commit",
            stderr="",
            exit_code=0,
            command="git reset --hard HEAD~1",
            success=True
        )

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git reset --hard HEAD~1"])
        
        # Verify complete workflow
        assert result.exit_code == 0
        assert "HEAD is now at abc1234" in result.stdout
        
        # Verify all workflow steps were called
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git reset --hard HEAD~1")
        mock_confirm.assert_called_once_with("This will permanently delete uncommitted changes")
        mock_execute.assert_called_once_with("git reset --hard HEAD~1")

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    def test_complete_dangerous_command_workflow_rejected(self, mock_confirm, mock_safety, mock_git_available):
        """Test complete workflow for dangerous command rejection."""
        # Setup mocks for dangerous command rejection
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["--force"],
            warning_message="This will force push and may overwrite remote changes"
        )
        mock_confirm.return_value = False

        # Execute dangerous command through CLI
        result = self.runner.invoke(app, ["--execute", "git push --force origin main"])
        
        # Verify workflow stops at confirmation
        assert result.exit_code == 0
        output = result.stdout + result.stderr
        assert "Command execution aborted by user" in output
        
        # Verify workflow steps up to confirmation
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git push --force origin main")
        mock_confirm.assert_called_once_with("This will force push and may overwrite remote changes")

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_complete_error_handling_workflow(self, mock_execute, mock_safety, mock_git_available):
        """Test complete workflow with Git command failure."""
        # Setup mocks for command failure
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="",
            stderr="fatal: not a git repository (or any of the parent directories): .git",
            exit_code=128,
            command="git status",
            success=False
        )

        # Execute command that will fail
        result = self.runner.invoke(app, ["--execute", "git status"])
        
        # Verify error handling workflow
        assert result.exit_code == 128
        output = result.stdout + result.stderr
        assert "Git repository error" in output
        assert "Command failed with exit code: 128" in output
        
        # Verify all workflow steps were called
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git status")
        mock_execute.assert_called_once_with("git status")

    @patch('git_gud.cli.is_git_available')
    def test_git_unavailable_workflow(self, mock_git_available):
        """Test workflow when Git is not available."""
        # Setup mock for Git unavailable
        mock_git_available.return_value = False

        # Execute command when Git is unavailable
        result = self.runner.invoke(app, ["--execute", "git status"])
        
        # Verify workflow stops at Git check
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Error: Git is not installed" in output
        assert "Please install Git" in output
        
        # Verify only Git availability was checked
        mock_git_available.assert_called_once()


class TestCLIErrorHandling:
    """Test cases for CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    def test_execute_command_safety_check_error(self, mock_safety, mock_git_available):
        """Test error handling when safety check fails."""
        mock_git_available.return_value = True
        mock_safety.side_effect = Exception("Safety check failed")

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Failed to analyze command safety" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    def test_execute_command_confirmation_error(self, mock_confirm, mock_safety, mock_git_available):
        """Test error handling when user confirmation fails."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["--force"],
            warning_message="Test warning"
        )
        mock_confirm.side_effect = Exception("Confirmation failed")

        result = self.runner.invoke(app, ["--execute", "git push --force"])
        
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Error during user confirmation" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_command_execution_error(self, mock_execute, mock_safety, mock_git_available):
        """Test error handling when command execution fails unexpectedly."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.side_effect = Exception("Execution failed")

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Unexpected error during command execution" in output

    def test_execute_command_empty_command(self):
        """Test error handling for empty command."""
        result = self.runner.invoke(app, ["--execute", ""])
        
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Empty command provided" in output

    def test_execute_command_whitespace_command(self):
        """Test error handling for whitespace-only command."""
        result = self.runner.invoke(app, ["--execute", "   \t\n   "])
        
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Empty command provided" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_command_git_not_found_error(self, mock_execute, mock_safety, mock_git_available):
        """Test specific error handling for Git not found."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="",
            stderr="Git executable not found",
            exit_code=127,
            command="git status",
            success=False
        )

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 127
        output = result.stdout + result.stderr
        assert "Git command not found" in output
        assert "ensure Git is properly installed" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_command_permission_denied_error(self, mock_execute, mock_safety, mock_git_available):
        """Test specific error handling for permission denied."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="",
            stderr="Permission denied",
            exit_code=126,
            command="git status",
            success=False
        )

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 126
        output = result.stdout + result.stderr
        assert "Permission denied" in output
        assert "Check your file permissions" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_command_timeout_error(self, mock_execute, mock_safety, mock_git_available):
        """Test specific error handling for command timeout."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="",
            stderr="Command timed out after 30 seconds",
            exit_code=124,
            command="git status",
            success=False
        )

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 124
        output = result.stdout + result.stderr
        assert "Command timed out" in output
        assert "took too long to complete" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_execute_command_git_repository_error(self, mock_execute, mock_safety, mock_git_available):
        """Test specific error handling for Git repository errors."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="",
            stderr="fatal: not a git repository (or any of the parent directories): .git",
            exit_code=128,
            command="git status",
            success=False
        )

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 128
        output = result.stdout + result.stderr
        assert "Git repository error" in output
        assert "not a Git repository" in output
        assert "git init" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.get_user_confirmation')
    def test_execute_command_keyboard_interrupt_during_confirmation(self, mock_confirm, mock_safety, mock_git_available):
        """Test handling of Ctrl+C during user confirmation."""
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["--force"],
            warning_message="Test warning"
        )
        mock_confirm.side_effect = KeyboardInterrupt()

        result = self.runner.invoke(app, ["--execute", "git push --force"])
        
        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "interrupted during confirmation" in output

    @patch('git_gud.cli.execute_command')
    def test_main_keyboard_interrupt_handling(self, mock_execute):
        """Test handling of Ctrl+C in main execution."""
        mock_execute.side_effect = KeyboardInterrupt()

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "interrupted by user" in output

    @patch('git_gud.cli.execute_command')
    def test_main_unexpected_error_handling(self, mock_execute):
        """Test handling of unexpected errors in main execution."""
        mock_execute.side_effect = RuntimeError("Unexpected error")

        result = self.runner.invoke(app, ["--execute", "git status"])
        
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Unexpected error occurred" in output

    @patch('git_gud.cli.is_git_available')
    @patch('git_gud.cli.check_command_safety')
    @patch('git_gud.cli.execute_git_command')
    def test_mixed_output_workflow(self, mock_execute, mock_safety, mock_git_available):
        """Test workflow with command that has both stdout and stderr."""
        # Setup mocks for command with mixed output
        mock_git_available.return_value = True
        mock_safety.return_value = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        mock_execute.return_value = GitResult(
            stdout="On branch main\nYour branch is up to date with 'origin/main'.",
            stderr="warning: LF will be replaced by CRLF",
            exit_code=0,
            command="git status",
            success=True
        )

        # Execute command with mixed output
        result = self.runner.invoke(app, ["--execute", "git status"])
        
        # Verify both outputs are displayed appropriately
        assert result.exit_code == 0
        assert "On branch main" in result.stdout
        # Note: stderr from Git command is not displayed for successful commands
        # This matches the current implementation behavior
        
        # Verify workflow completed
        mock_git_available.assert_called_once()
        mock_safety.assert_called_once_with("git status")
        mock_execute.assert_called_once_with("git status")