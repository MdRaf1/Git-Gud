"""
Tests for AI module with context awareness.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from git_sensei.ai import translate_to_git, translate_to_git_sync


class TestAIWithContext:
    """Test cases for AI module with context awareness."""

    @pytest.mark.asyncio
    @patch("git_sensei.ai.AsyncOpenAI")
    async def test_translate_to_git_with_context(self, mock_openai_class):
        """Test AI translation with repository context."""
        # Mock the OpenAI client and response
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "git add . && git commit -m 'fix bug'"
        )
        mock_client.chat.completions.create.return_value = mock_response

        # Set up environment variable
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
            context = "Status:\nM  file1.py\n\nCurrent branch: main\n\nRecent commits:\nabc123 Latest commit"
            result = await translate_to_git("commit my changes", context)

        assert result == "git add . && git commit -m 'fix bug'"

        # Verify the API was called with context-aware prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        system_message = messages[0]["content"]

        assert "repository context" in system_message.lower()
        assert "Status:" in system_message
        assert "M  file1.py" in system_message
        assert "Current branch: main" in system_message

    @pytest.mark.asyncio
    @patch("git_sensei.ai.AsyncOpenAI")
    async def test_translate_to_git_without_context(self, mock_openai_class):
        """Test AI translation without repository context."""
        # Mock the OpenAI client and response
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "git status"
        mock_client.chat.completions.create.return_value = mock_response

        # Set up environment variable
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
            result = await translate_to_git("show me the status")

        assert result == "git status"

        # Verify the API was called with basic prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        system_message = messages[0]["content"]

        assert "repository context" not in system_message.lower()
        assert "translate the following user request" in system_message.lower()

    @patch("git_sensei.ai.asyncio.run")
    def test_translate_to_git_sync_with_context(self, mock_asyncio_run):
        """Test synchronous wrapper with context."""
        mock_asyncio_run.return_value = "git add ."

        context = "Status:\nM  file1.py"
        result = translate_to_git_sync("add my changes", context)

        assert result == "git add ."
        # Verify asyncio.run was called with both phrase and context
        mock_asyncio_run.assert_called_once()

    @patch("git_sensei.ai.asyncio.run")
    def test_translate_to_git_sync_without_context(self, mock_asyncio_run):
        """Test synchronous wrapper without context."""
        mock_asyncio_run.return_value = "git status"

        result = translate_to_git_sync("show status")

        assert result == "git status"
        mock_asyncio_run.assert_called_once()
