"""
Integration tests for Phase 2 AI functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from click.exceptions import Exit

from git_sensei.ai import translate_to_git_sync
from git_sensei.cli import execute_natural_language


class TestPhase2Integration:
    """Test Phase 2 AI integration with existing safety and execution systems."""

    def test_ai_translation_success(self):
        """Test successful AI translation."""
        with patch("git_sensei.ai.AsyncOpenAI") as mock_client_class:
            # Setup mock
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "git status"

            async def mock_create(*_args, **_kwargs):
                return mock_response

            mock_client.chat.completions.create = mock_create

            # Set API key
            os.environ["OPENROUTER_API_KEY"] = "test-key"

            try:
                result = translate_to_git_sync("show me the current status")
                assert result == "git status"
            finally:
                del os.environ["OPENROUTER_API_KEY"]

    def test_ai_translation_no_api_key(self):
        """Test AI translation fails without API key."""
        # Ensure no API key is set
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            translate_to_git_sync("show me the current status")

    def test_ai_translation_empty_phrase(self):
        """Test AI translation fails with empty phrase."""
        os.environ["OPENROUTER_API_KEY"] = "test-key"

        try:
            with pytest.raises(ValueError, match="Empty phrase"):
                translate_to_git_sync("")
        finally:
            del os.environ["OPENROUTER_API_KEY"]

    def test_natural_language_to_safe_command_workflow(self):
        """Test complete workflow from natural language to safe command execution."""
        with patch("git_sensei.cli.translate_to_git_sync") as mock_translate, patch(
            "git_sensei.cli.execute_command"
        ) as mock_execute:

            # Mock translation to safe command
            mock_translate.return_value = "git status"

            # Execute natural language
            try:
                execute_natural_language("show me the current status")
            except SystemExit:
                pass  # Expected from CLI

            # Verify workflow - now includes context parameter
            assert mock_translate.call_count == 1
            call_args = mock_translate.call_args
            assert (
                call_args[0][0] == "show me the current status"
            )  # First argument is phrase
            assert len(call_args[0]) == 2  # Should have phrase and context
            mock_execute.assert_called_once_with("git status")

    def test_natural_language_to_dangerous_command_workflow(self):
        """Test workflow when AI translates to dangerous command."""
        with patch("git_sensei.cli.translate_to_git_sync") as mock_translate, patch(
            "git_sensei.cli.execute_command"
        ) as mock_execute:

            # Mock translation to dangerous command
            mock_translate.return_value = "git push --force origin main"

            # Execute natural language
            try:
                execute_natural_language("force push to main")
            except SystemExit:
                pass  # Expected from CLI

            # Verify workflow - dangerous command should still be passed to execute_command
            # where safety checks will handle it
            assert mock_translate.call_count == 1
            call_args = mock_translate.call_args
            assert call_args[0][0] == "force push to main"  # First argument is phrase
            assert len(call_args[0]) == 2  # Should have phrase and context
            mock_execute.assert_called_once_with("git push --force origin main")

    def test_natural_language_translation_error_handling(self):
        """Test error handling when AI translation fails."""
        with patch("git_sensei.cli.translate_to_git_sync") as mock_translate:
            # Mock translation failure
            mock_translate.side_effect = Exception("API error")

            # Execute natural language - should handle error gracefully
            # typer raises click.exceptions.Exit, not SystemExit
            with pytest.raises(Exit):
                execute_natural_language("show me the current status")

            assert mock_translate.call_count == 1
            call_args = mock_translate.call_args
            assert (
                call_args[0][0] == "show me the current status"
            )  # First argument is phrase
            assert len(call_args[0]) == 2  # Should have phrase and context

    def test_openai_client_configuration(self):
        """Test that OpenAI client is configured correctly for OpenRouter."""
        with patch("git_sensei.ai.AsyncOpenAI") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "git status"

            async def mock_create(*_args, **_kwargs):
                return mock_response

            mock_client.chat.completions.create = mock_create

            os.environ["OPENROUTER_API_KEY"] = "test-key"

            try:
                translate_to_git_sync("test phrase")

                # Verify client was configured with OpenRouter settings
                mock_client_class.assert_called_once_with(
                    base_url="https://openrouter.ai/api/v1", api_key="test-key"
                )
            finally:
                del os.environ["OPENROUTER_API_KEY"]
