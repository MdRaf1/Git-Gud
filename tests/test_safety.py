"""
Unit tests for safety module data models and functions.
"""

import pytest
from git_gud.safety import SafetyCheck, load_dangerous_patterns, check_command_safety, get_user_confirmation
from unittest.mock import patch, MagicMock
import typer


class TestSafetyCheck:
    """Test cases for SafetyCheck dataclass."""
    
    def test_safety_check_creation_safe(self):
        """Test creating SafetyCheck for safe command."""
        check = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        
        assert check.is_safe is True
        assert check.dangerous_patterns == []
        assert check.warning_message == ""
    
    def test_safety_check_creation_dangerous(self):
        """Test creating SafetyCheck for dangerous command."""
        patterns = ["push.*force", "reset.*hard"]
        warning = "This command contains dangerous operations"
        
        check = SafetyCheck(
            is_safe=False,
            dangerous_patterns=patterns,
            warning_message=warning
        )
        
        assert check.is_safe is False
        assert check.dangerous_patterns == patterns
        assert check.warning_message == warning
    
    def test_safety_check_field_types(self):
        """Test that SafetyCheck fields have correct types."""
        check = SafetyCheck(
            is_safe=False,
            dangerous_patterns=["test_pattern"],
            warning_message="test warning"
        )
        
        assert isinstance(check.is_safe, bool)
        assert isinstance(check.dangerous_patterns, list)
        assert isinstance(check.warning_message, str)
    
    def test_safety_check_empty_patterns(self):
        """Test SafetyCheck with empty patterns list."""
        check = SafetyCheck(
            is_safe=True,
            dangerous_patterns=[],
            warning_message=""
        )
        
        assert len(check.dangerous_patterns) == 0
        assert check.dangerous_patterns == []
    
    def test_safety_check_multiple_patterns(self):
        """Test SafetyCheck with multiple dangerous patterns."""
        patterns = ["push.*force", "reset.*hard", "filter-branch"]
        
        check = SafetyCheck(
            is_safe=False,
            dangerous_patterns=patterns,
            warning_message="Multiple dangerous operations detected"
        )
        
        assert len(check.dangerous_patterns) == 3
        assert "push.*force" in check.dangerous_patterns
        assert "reset.*hard" in check.dangerous_patterns
        assert "filter-branch" in check.dangerous_patterns


class TestLoadDangerousPatterns:
    """Test cases for load_dangerous_patterns function."""
    
    def test_load_dangerous_patterns_returns_list(self):
        """Test that load_dangerous_patterns returns a list."""
        patterns = load_dangerous_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
    
    def test_load_dangerous_patterns_contains_expected_patterns(self):
        """Test that dangerous patterns include expected operations."""
        patterns = load_dangerous_patterns()
        
        # Check for key dangerous patterns
        force_push_pattern = any("push" in pattern and "force" in pattern for pattern in patterns)
        reset_hard_pattern = any("reset" in pattern and "hard" in pattern for pattern in patterns)
        filter_branch_pattern = any("filter-branch" in pattern for pattern in patterns)
        
        assert force_push_pattern, "Should include force push pattern"
        assert reset_hard_pattern, "Should include reset hard pattern"
        assert filter_branch_pattern, "Should include filter-branch pattern"
    
    def test_load_dangerous_patterns_all_strings(self):
        """Test that all patterns are strings."""
        patterns = load_dangerous_patterns()
        
        for pattern in patterns:
            assert isinstance(pattern, str)
            assert len(pattern) > 0


class TestCheckCommandSafety:
    """Test cases for check_command_safety function."""
    
    def test_check_safe_command_status(self):
        """Test safety check for safe git status command."""
        result = check_command_safety("git status")
        
        assert isinstance(result, SafetyCheck)
        assert result.is_safe is True
        assert result.dangerous_patterns == []
        assert result.warning_message == ""
    
    def test_check_safe_command_log(self):
        """Test safety check for safe git log command."""
        result = check_command_safety("git log --oneline")
        
        assert result.is_safe is True
        assert len(result.dangerous_patterns) == 0
    
    def test_check_safe_command_diff(self):
        """Test safety check for safe git diff command."""
        result = check_command_safety("git diff HEAD~1")
        
        assert result.is_safe is True
        assert result.dangerous_patterns == []
    
    def test_check_dangerous_command_force_push(self):
        """Test safety check for dangerous force push command."""
        result = check_command_safety("git push --force origin main")
        
        assert isinstance(result, SafetyCheck)
        assert result.is_safe is False
        assert len(result.dangerous_patterns) > 0
        assert result.warning_message != ""
        assert "force push" in result.warning_message.lower()
    
    def test_check_dangerous_command_reset_hard(self):
        """Test safety check for dangerous reset hard command."""
        result = check_command_safety("git reset --hard HEAD~1")
        
        assert result.is_safe is False
        assert len(result.dangerous_patterns) > 0
        assert "reset" in result.warning_message.lower()
    
    def test_check_dangerous_command_filter_branch(self):
        """Test safety check for dangerous filter-branch command."""
        result = check_command_safety("git filter-branch --tree-filter 'rm -f passwords.txt' HEAD")
        
        assert result.is_safe is False
        assert len(result.dangerous_patterns) > 0
        assert "history" in result.warning_message.lower()
    
    def test_check_dangerous_command_clean_force(self):
        """Test safety check for dangerous clean force command."""
        result = check_command_safety("git clean -fd")
        
        assert result.is_safe is False
        assert len(result.dangerous_patterns) > 0
        assert "delete" in result.warning_message.lower()
    
    def test_check_command_case_insensitive(self):
        """Test that command safety check is case insensitive."""
        result_lower = check_command_safety("git push --force")
        result_upper = check_command_safety("GIT PUSH --FORCE")
        result_mixed = check_command_safety("Git Push --Force")
        
        assert result_lower.is_safe is False
        assert result_upper.is_safe is False
        assert result_mixed.is_safe is False
    
    def test_check_command_with_git_prefix(self):
        """Test command safety with and without git prefix."""
        result_with_git = check_command_safety("git push --force")
        result_without_git = check_command_safety("push --force")
        
        assert result_with_git.is_safe is False
        assert result_without_git.is_safe is False
    
    def test_check_command_multiple_dangerous_patterns(self):
        """Test command with multiple dangerous patterns."""
        # This is a contrived example, but tests the logic
        result = check_command_safety("git reset --hard && git push --force")
        
        assert result.is_safe is False
        # Should detect at least one dangerous pattern
        assert len(result.dangerous_patterns) > 0
    
    def test_check_empty_command(self):
        """Test safety check for empty command."""
        result = check_command_safety("")
        
        assert result.is_safe is True
        assert result.dangerous_patterns == []
        assert result.warning_message == ""
    
    def test_check_whitespace_command(self):
        """Test safety check for whitespace-only command."""
        result = check_command_safety("   \t\n   ")
        
        assert result.is_safe is True
        assert result.dangerous_patterns == []


class TestGetUserConfirmation:
    """Test cases for get_user_confirmation function."""
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_yes(self, mock_echo, mock_prompt):
        """Test user confirmation with 'yes' response."""
        mock_prompt.return_value = "yes"
        
        result = get_user_confirmation("Test warning message")
        
        assert result is True
        mock_prompt.assert_called_once()
        # Verify that warning messages are displayed
        assert mock_echo.call_count > 0
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_no(self, mock_echo, mock_prompt):
        """Test user confirmation with 'no' response."""
        mock_prompt.return_value = "no"
        
        result = get_user_confirmation("Test warning message")
        
        assert result is False
        mock_prompt.assert_called_once()
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_other_response(self, mock_echo, mock_prompt):
        """Test user confirmation with other response."""
        mock_prompt.return_value = "maybe"
        
        result = get_user_confirmation("Test warning message")
        
        assert result is False
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_case_insensitive(self, mock_echo, mock_prompt):
        """Test user confirmation is case insensitive for 'yes'."""
        test_cases = ["YES", "Yes", "YeS", "yes"]
        
        for response in test_cases:
            mock_prompt.return_value = response
            result = get_user_confirmation("Test warning")
            assert result is True, f"Failed for response: {response}"
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_whitespace_handling(self, mock_echo, mock_prompt):
        """Test user confirmation handles whitespace correctly."""
        mock_prompt.return_value = "  yes  "
        
        result = get_user_confirmation("Test warning message")
        
        assert result is True
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_displays_warning(self, mock_echo, mock_prompt):
        """Test that user confirmation displays the warning message."""
        warning_message = "This is a test warning about dangerous operations"
        mock_prompt.return_value = "no"
        
        get_user_confirmation(warning_message)
        
        # Check that the warning message was displayed
        echo_calls = [call[0][0] for call in mock_echo.call_args_list]
        warning_displayed = any(warning_message in call for call in echo_calls)
        assert warning_displayed, "Warning message should be displayed to user"
    
    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_displays_danger_header(self, mock_echo, mock_prompt):
        """Test that user confirmation displays danger warning header."""
        mock_prompt.return_value = "no"
        
        get_user_confirmation("Test warning")
        
        # Check that danger warning is displayed
        echo_calls = [call[0][0] for call in mock_echo.call_args_list]
        danger_displayed = any("DANGEROUS OPERATION" in call for call in echo_calls)
        assert danger_displayed, "Danger warning should be displayed"


class TestWarningMessageGeneration:
    """Test cases for warning message generation."""
    
    def test_force_push_warning_message(self):
        """Test warning message for force push operations."""
        result = check_command_safety("git push --force")
        
        assert "force push" in result.warning_message.lower()
        assert "overwriting" in result.warning_message.lower() or "history" in result.warning_message.lower()
    
    def test_reset_hard_warning_message(self):
        """Test warning message for reset hard operations."""
        result = check_command_safety("git reset --hard")
        
        assert "discard" in result.warning_message.lower() or "reset" in result.warning_message.lower()
        assert "working directory" in result.warning_message.lower() or "changes" in result.warning_message.lower()
    
    def test_filter_branch_warning_message(self):
        """Test warning message for filter-branch operations."""
        result = check_command_safety("git filter-branch --tree-filter 'rm file'")
        
        assert "history" in result.warning_message.lower()
        assert "rewrite" in result.warning_message.lower()
    
    def test_clean_force_warning_message(self):
        """Test warning message for clean force operations."""
        result = check_command_safety("git clean -fd")
        
        assert "delete" in result.warning_message.lower()
        assert "untracked" in result.warning_message.lower() or "files" in result.warning_message.lower()


class TestGetUserConfirmationErrorHandling:
    """Test cases for error handling in get_user_confirmation function."""

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_keyboard_interrupt(self, mock_echo, mock_prompt):
        """Test user confirmation with KeyboardInterrupt (Ctrl+C)."""
        mock_prompt.side_effect = KeyboardInterrupt()
        
        with pytest.raises(KeyboardInterrupt):
            get_user_confirmation("Test warning message")
        
        mock_prompt.assert_called_once()

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_eof_error(self, mock_echo, mock_prompt):
        """Test user confirmation with EOFError."""
        mock_prompt.side_effect = EOFError()
        
        result = get_user_confirmation("Test warning message")
        
        assert result is False
        mock_prompt.assert_called_once()
        # Check that appropriate error message was displayed
        error_calls = [call for call in mock_echo.call_args_list if "No input received" in str(call)]
        assert len(error_calls) > 0

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_prompt_error(self, mock_echo, mock_prompt):
        """Test user confirmation with prompt error."""
        mock_prompt.side_effect = Exception("Prompt failed")
        
        result = get_user_confirmation("Test warning message")
        
        assert result is False
        mock_prompt.assert_called_once()
        # Check that error handling message was displayed
        error_calls = [call for call in mock_echo.call_args_list if "Error reading user input" in str(call)]
        assert len(error_calls) > 0

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_unexpected_error(self, mock_echo, mock_prompt):
        """Test user confirmation with unexpected error during display."""
        # Make echo fail to test error handling
        mock_echo.side_effect = [None, None, None, Exception("Display failed")] + [None] * 10
        mock_prompt.return_value = "yes"
        
        result = get_user_confirmation("Test warning message")
        
        # Should still handle the error gracefully
        assert result is False
        # Check that error handling was triggered
        final_calls = [call for call in mock_echo.call_args_list if "Unexpected error" in str(call)]
        assert len(final_calls) > 0

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_ctrl_c_message_displayed(self, mock_echo, mock_prompt):
        """Test that Ctrl+C instruction is displayed to user."""
        mock_prompt.return_value = "no"
        
        get_user_confirmation("Test warning message")
        
        # Check that Ctrl+C instruction was displayed
        ctrl_c_calls = [call for call in mock_echo.call_args_list if "Ctrl+C" in str(call)]
        assert len(ctrl_c_calls) > 0

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_empty_warning_message(self, mock_echo, mock_prompt):
        """Test user confirmation with empty warning message."""
        mock_prompt.return_value = "no"
        
        result = get_user_confirmation("")
        
        assert result is False
        # Should still display the confirmation prompt
        mock_prompt.assert_called_once()

    @patch('typer.prompt')
    @patch('typer.echo')
    def test_get_user_confirmation_none_warning_message(self, mock_echo, mock_prompt):
        """Test user confirmation with None warning message."""
        mock_prompt.return_value = "no"
        
        # This should handle None gracefully
        result = get_user_confirmation(None)
        
        assert result is False
        mock_prompt.assert_called_once()


class TestSafetyModuleErrorHandling:
    """Test cases for error handling in safety module functions."""

    def test_check_command_safety_none_command(self):
        """Test safety check with None command."""
        result = check_command_safety(None)
        
        # Should handle None gracefully and treat as safe
        assert isinstance(result, SafetyCheck)
        assert result.is_safe is True
        assert result.dangerous_patterns == []

    @patch('git_gud.safety.load_dangerous_patterns')
    def test_check_command_safety_pattern_loading_error(self, mock_load_patterns):
        """Test safety check when pattern loading fails."""
        mock_load_patterns.side_effect = Exception("Pattern loading failed")
        
        # Should handle the error gracefully
        result = check_command_safety("git status")
        
        # The function should still work, possibly with empty patterns
        assert isinstance(result, SafetyCheck)

    def test_load_dangerous_patterns_consistency(self):
        """Test that load_dangerous_patterns is consistent across calls."""
        patterns1 = load_dangerous_patterns()
        patterns2 = load_dangerous_patterns()
        
        assert patterns1 == patterns2
        assert len(patterns1) > 0

    @patch('re.search')
    def test_check_command_safety_regex_error(self, mock_search):
        """Test safety check when regex search fails."""
        mock_search.side_effect = Exception("Regex error")
        
        # Should handle regex errors gracefully
        result = check_command_safety("git status")
        
        assert isinstance(result, SafetyCheck)
        # Should default to safe if regex fails
        assert result.is_safe is True