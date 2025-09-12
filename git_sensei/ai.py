"""
AI module for Git sensei.

This module handles interactions with the OpenRouter API to translate
natural language phrases into Git commands.
"""

import asyncio
import concurrent.futures
import os

from openai import AsyncOpenAI


class GitsenseiAIError(Exception):
    """Custom exception for Git sensei AI-related errors."""


async def translate_to_git(phrase: str, context: str = "") -> str:
    """
    Translate a natural language phrase into a Git command using OpenRouter API.

    Args:
        phrase: Natural language description of what the user wants to do
        context: Repository context information to help AI make better decisions

    Returns:
        A Git command string that accomplishes the requested action

    Raises:
        ValueError: If API key is not found or phrase is empty
        GitsenseiAIError: If API call fails
    """
    if not phrase or not phrase.strip():
        raise ValueError("Empty phrase provided")

    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not found")

    # Initialize OpenAI client with OpenRouter configuration
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # System prompt for Git command translation with context awareness
    if context:
        system_prompt = (
            "You are an expert Git assistant. Your task is to translate the "
            "user's request into the single most logical and appropriate Git "
            "command based on the provided repository context.\n\n"
            "Key Instructions:\n"
            "- Use the repository context to make intelligent decisions.\n"
            "- If the user wants to commit but there are no staged files, "
            "suggest adding them first.\n"
            "- If the user's intent is ambiguous, choose the most common and "
            "safest Git command that fits the context.\n"
            "- Always return only the single, best, executable command. Do not "
            "add any explanation, decoration, or code fences.\n\n"
            f"Repository Context:\n```\n{context}\n```\n\n"
            f"User Request: {phrase}"
        )
        user_message = phrase
    else:
        system_prompt = (
            "You are an expert Git assistant. Your task is to translate the "
            "following user request into a single, executable Git command. "
            "Return only the command, with no explanation, decoration, or "
            "code fences."
        )
        user_message = phrase

    try:
        # Make API call with custom headers
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/MdRaf1/Git-sensei/",
                "X-Title": "Git sensei",
            },
        )

        # Extract the command from the response
        if response.choices and response.choices[0].message:
            command = response.choices[0].message.content
            if command:
                return command.strip()

        raise GitsenseiAIError("No valid response received from AI")

    except Exception as e:
        raise GitsenseiAIError(
            f"Failed to translate phrase to Git command: {str(e)}"
        ) from e


def translate_to_git_sync(phrase: str, context: str = "") -> str:
    """
    Synchronous wrapper for translate_to_git function.

    Args:
        phrase: Natural language description of what the user wants to do
        context: Repository context information to help AI make better decisions

    Returns:
        A Git command string that accomplishes the requested action
    """
    try:
        # Run the async function in a new event loop
        return asyncio.run(translate_to_git(phrase, context))
    except RuntimeError:
        # If we're already in an event loop, create a new one in a thread

        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(translate_to_git(phrase, context))
            finally:
                loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()
