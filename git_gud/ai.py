"""
AI module for Git Gud.

This module handles interactions with the OpenRouter API to translate
natural language phrases into Git commands.
"""

import os
from typing import Optional
import asyncio
from openai import AsyncOpenAI


async def translate_to_git(phrase: str) -> str:
    """
    Translate a natural language phrase into a Git command using OpenRouter API.
    
    Args:
        phrase: Natural language description of what the user wants to do
        
    Returns:
        A Git command string that accomplishes the requested action
        
    Raises:
        ValueError: If API key is not found or phrase is empty
        Exception: If API call fails
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
    
    # System prompt for Git command translation
    system_prompt = (
        "You are an expert Git assistant. Your task is to translate the following "
        "user request into a single, executable Git command. Return only the command, "
        "with no explanation, decoration, or code fences."
    )
    
    try:
        # Make API call with custom headers
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": phrase}
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/MdRaf1/Git-Gud/",
                "X-Title": "Git Gud"
            }
        )
        
        # Extract the command from the response
        if response.choices and response.choices[0].message:
            command = response.choices[0].message.content
            if command:
                return command.strip()
        
        raise Exception("No valid response received from AI")
        
    except Exception as e:
        raise Exception(f"Failed to translate phrase to Git command: {str(e)}")


def translate_to_git_sync(phrase: str) -> str:
    """
    Synchronous wrapper for translate_to_git function.
    
    Args:
        phrase: Natural language description of what the user wants to do
        
    Returns:
        A Git command string that accomplishes the requested action
    """
    try:
        # Run the async function in a new event loop
        return asyncio.run(translate_to_git(phrase))
    except RuntimeError:
        # If we're already in an event loop, create a new one in a thread
        import concurrent.futures
        import threading
        
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(translate_to_git(phrase))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()