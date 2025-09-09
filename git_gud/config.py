"""
Configuration module for Git Gud.

This module handles application configuration and settings management,
providing extensibility for future features and customization.
"""

from typing import Dict, Any, List
import os
from pathlib import Path


def load_config() -> Dict[str, Any]:
    """
    Load application configuration.
    
    Returns:
        Dictionary containing application configuration settings
    """
    # Default configuration
    config = {
        "timeout": 30,
        "require_confirmation": True,
        "verbose": False,
        "custom_dangerous_patterns": [],
    }
    
    # TODO: In future versions, load from config file
    # config_file = Path.home() / ".git-gud" / "config.json"
    # if config_file.exists():
    #     with open(config_file, 'r') as f:
    #         user_config = json.load(f)
    #         config.update(user_config)
    
    return config


def get_dangerous_patterns() -> List[str]:
    """
    Get configured dangerous patterns.
    
    Returns:
        List of dangerous Git operation patterns
    """
    from .safety import load_dangerous_patterns
    
    try:
        patterns = load_dangerous_patterns()
    except Exception:
        patterns = []
    
    try:
        config = load_config()
        # Add any custom patterns from configuration
        custom_patterns = config.get("custom_dangerous_patterns", [])
        patterns.extend(custom_patterns)
    except Exception:
        # If config loading fails, just return the default patterns
        pass
    
    return patterns


def get_timeout() -> int:
    """
    Get configured command timeout.
    
    Returns:
        Timeout value in seconds
    """
    try:
        config = load_config()
        timeout = config.get("timeout", 30)
        return timeout if timeout is not None else 30
    except Exception:
        return 30


def should_require_confirmation() -> bool:
    """
    Check if dangerous operations should require confirmation.
    
    Returns:
        True if confirmation is required, False otherwise
    """
    try:
        config = load_config()
        confirmation = config.get("require_confirmation", True)
        return confirmation if confirmation is not None else True
    except Exception:
        return True