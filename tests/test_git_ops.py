"""
Unit tests for git_ops module data models and functions.
"""

import pytest
from git_gud.git_ops import GitResult, is_git_available, get_git_version, execute_git_command
from unittest.mock import patch, MagicMock
import subprocess


class TestGitResult:
    """Test cases for GitResult dataclass."""
    
    def test_git_result_creation_success(self):
        """Test creating GitResult with successful command."""
        result = GitResult(
            stdout="On branch main\nnothing to commit, working tree clean",
            stderr="",
            exit_code=0,
            command="git status",
            success=True
        )
        
        assert result.stdout == "On branch main\nnothing to commit, working tree clean"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.command == "git status"
        assert result.success is True
    
    def test_git_result_creation_failure(self):
        """Test creating GitResult with failed command."""
        result = GitResult(
            stdout="",
            stderr="fatal: not a git repository",
            exit_code=128,
            command="git status",
            success=False
        )
        
        assert result.stdout == ""
        assert result.stderr == "fatal: not a git repository"
        assert result.exit_code == 128
        assert result.command == "git status"
        assert result.success is False
    
    def test_git_result_with_both_outputs(self):
        """Test GitResult with both stdout and stderr."""
        result = GitResult(
            stdout="Some output",
            stderr="Some warning",
            exit_code=0,
            command="git log --oneline",
            success=True
        )
        
        assert result.stdout == "Some output"
        assert result.stderr == "Some warning"
        assert result.exit_code == 0
        assert result.success is True
    
    def test_git_result_field_types(self):
        """Test that GitResult fields have correct types."""
        result = GitResult(
            stdout="test",
            stderr="test",
            exit_code=1,
            command="test",
            success=False
        )
        
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)
        assert isinstance(result.exit_code, int)
        assert isinstance(result.command, str)
        assert isinstance(result.success, bool)
    
    def test_git_result_empty_strings(self):
        """Test GitResult with empty string values."""
        result = GitResult(
            stdout="",
            stderr="",
            exit_code=0,
            command="",
            success=True
        )
        
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.command == ""
        assert result.success is True
    
    def test_git_result_multiline_output(self):
        """Test GitResult with multiline output."""
        multiline_output = """commit abc123
Author: Test User <test@example.com>
Date: Mon Jan 1 12:00:00 2024 +0000

    Initial commit"""
        
        result = GitResult(
            stdout=multiline_output,
            stderr="",
            exit_code=0,
            command="git log -1",
            success=True
        )
        
        assert result.stdout == multiline_output
        assert "\n" in result.stdout
        assert "Initial commit" in result.stdout


class TestGitAvailability:
    """Test cases for Git availability functions."""
    
    @patch('shutil.which')
    def test_is_git_available_true(self, mock_which):
        """Test is_git_available when Git is installed."""
        mock_which.return_value = "/usr/bin/git"
        
        assert is_git_available() is True
        mock_which.assert_called_once_with("git")
    
    @patch('shutil.which')
    def test_is_git_available_false(self, mock_which):
        """Test is_git_available when Git is not installed."""
        mock_which.return_value = None
        
        assert is_git_available() is False
        mock_which.assert_called_once_with("git")
    
    @patch('git_gud.git_ops.is_git_available')
    def test_get_git_version_not_available(self, mock_is_available):
        """Test get_git_version when Git is not available."""
        mock_is_available.return_value = False
        
        result = get_git_version()
        
        assert result is None
        mock_is_available.assert_called_once()
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_get_git_version_success(self, mock_run, mock_is_available):
        """Test get_git_version with successful execution."""
        mock_is_available.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "git version 2.34.1\n"
        mock_run.return_value = mock_result
        
        result = get_git_version()
        
        assert result == "git version 2.34.1"
        mock_run.assert_called_once_with(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_get_git_version_subprocess_error(self, mock_run, mock_is_available):
        """Test get_git_version with subprocess error."""
        mock_is_available.return_value = True
        mock_run.side_effect = subprocess.SubprocessError("Test error")
        
        result = get_git_version()
        
        assert result is None


class TestExecuteGitCommand:
    """Test cases for execute_git_command function."""
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_success(self, mock_run, mock_git_available):
        """Test successful Git command execution."""
        mock_git_available.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "On branch main"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.stdout == "On branch main"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.command == "status"
        assert result.success is True
        
        mock_run.assert_called_once_with(
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False
        )
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_with_git_prefix(self, mock_run, mock_git_available):
        """Test command execution with 'git' prefix in command."""
        mock_git_available.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = execute_git_command("git status")
        
        assert result.command == "git status"
        mock_run.assert_called_once_with(
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False
        )
    
    @patch('subprocess.run')
    def test_execute_git_command_failure(self, mock_run):
        """Test failed Git command execution."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "fatal: not a git repository"
        mock_result.returncode = 128
        mock_run.return_value = mock_result
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.stdout == ""
        assert result.stderr == "fatal: not a git repository"
        assert result.exit_code == 128
        assert result.success is False
    
    @patch('subprocess.run')
    def test_execute_git_command_timeout(self, mock_run):
        """Test Git command execution timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "status"], 30)
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.stdout == ""
        assert "timed out after 30 seconds" in result.stderr
        assert result.exit_code == 124
        assert result.success is False
    
    @patch('subprocess.run')
    def test_execute_git_command_subprocess_error(self, mock_run):
        """Test Git command execution with subprocess error."""
        mock_run.side_effect = subprocess.SubprocessError("Test error")
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.stdout == ""
        assert "Subprocess error occurred: Test error" in result.stderr
        assert result.exit_code == 1
        assert result.success is False
    
    @patch('subprocess.run')
    def test_execute_git_command_custom_timeout(self, mock_run):
        """Test Git command execution with custom timeout."""
        mock_result = MagicMock()
        mock_result.stdout = "test"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = execute_git_command("status", timeout=60)
        
        mock_run.assert_called_once_with(
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=60,
            shell=False
        )
    
    @patch('subprocess.run')
    def test_execute_git_command_complex_command(self, mock_run):
        """Test execution of complex Git command with multiple arguments."""
        mock_result = MagicMock()
        mock_result.stdout = "commit log"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = execute_git_command("log --oneline -n 5")
        
        mock_run.assert_called_once_with(
            ["git", "log", "--oneline", "-n", "5"],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False
        )
        
        assert result.command == "log --oneline -n 5"


class TestExecuteGitCommandErrorHandling:
    """Test cases for error handling in execute_git_command function."""
    
    @patch('git_gud.git_ops.is_git_available')
    def test_execute_git_command_git_not_available(self, mock_git_available):
        """Test command execution when Git is not available."""
        mock_git_available.return_value = False
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 127
        assert "Git is not installed" in result.stderr
        assert result.stdout == ""
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    def test_execute_git_command_empty_command(self, mock_git_available):
        """Test command execution with empty command."""
        mock_git_available.return_value = True
        
        result = execute_git_command("")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Empty command provided" in result.stderr
        assert result.command == ""
    
    @patch('git_gud.git_ops.is_git_available')
    def test_execute_git_command_whitespace_only_command(self, mock_git_available):
        """Test command execution with whitespace-only command."""
        mock_git_available.return_value = True
        
        result = execute_git_command("   \t\n   ")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Empty command provided" in result.stderr
    
    @patch('git_gud.git_ops.is_git_available')
    def test_execute_git_command_git_only_command(self, mock_git_available):
        """Test command execution with only 'git' as command."""
        mock_git_available.return_value = True
        
        result = execute_git_command("git")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Invalid Git command format" in result.stderr
        assert result.command == "git"
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_file_not_found_error(self, mock_run, mock_git_available):
        """Test command execution with FileNotFoundError."""
        mock_git_available.return_value = True
        mock_run.side_effect = FileNotFoundError("Git executable not found")
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 127
        assert "Git executable not found" in result.stderr
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_permission_error(self, mock_run, mock_git_available):
        """Test command execution with PermissionError."""
        mock_git_available.return_value = True
        mock_run.side_effect = PermissionError("Permission denied")
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 126
        assert "Permission denied" in result.stderr
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_os_error(self, mock_run, mock_git_available):
        """Test command execution with OSError."""
        mock_git_available.return_value = True
        mock_run.side_effect = OSError("System error occurred")
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "System error occurred" in result.stderr
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_timeout_improved_message(self, mock_run, mock_git_available):
        """Test improved timeout error message."""
        mock_git_available.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "status"], 30)
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 124
        assert "timed out after 30 seconds" in result.stderr
        assert "may be waiting for input" in result.stderr
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_subprocess_error_improved(self, mock_run, mock_git_available):
        """Test improved subprocess error handling."""
        mock_git_available.return_value = True
        mock_run.side_effect = subprocess.SubprocessError("Subprocess failed")
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Subprocess error occurred" in result.stderr
        assert "Subprocess failed" in result.stderr
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    @patch('subprocess.run')
    def test_execute_git_command_unexpected_error(self, mock_run, mock_git_available):
        """Test handling of unexpected errors."""
        mock_git_available.return_value = True
        mock_run.side_effect = RuntimeError("Unexpected error")
        
        result = execute_git_command("status")
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Unexpected error occurred" in result.stderr
        assert "Unexpected error" in result.stderr
        assert result.command == "status"
    
    @patch('git_gud.git_ops.is_git_available')
    def test_execute_git_command_none_command(self, mock_git_available):
        """Test error handling with None command."""
        mock_git_available.return_value = True
        
        result = execute_git_command(None)
        
        assert isinstance(result, GitResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Empty command provided" in result.stderr