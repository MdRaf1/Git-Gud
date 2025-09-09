"""
Unit tests for config module.

Tests configuration loading, dangerous patterns management, and settings.
"""

import pytest
from unittest.mock import patch, MagicMock
from git_gud.config import load_config, get_dangerous_patterns, get_timeout, should_require_confirmation


class TestLoadConfig:
    """Test cases for load_config function."""
    
    def test_load_config_returns_dict(self):
        """Test that load_config returns a dictionary."""
        config = load_config()
        
        assert isinstance(config, dict)
        assert len(config) > 0
    
    def test_load_config_default_values(self):
        """Test that load_config returns expected default values."""
        config = load_config()
        
        assert config["timeout"] == 30
        assert config["require_confirmation"] is True
        assert config["verbose"] is False
        assert config["custom_dangerous_patterns"] == []
    
    def test_load_config_contains_required_keys(self):
        """Test that load_config contains all required configuration keys."""
        config = load_config()
        
        required_keys = ["timeout", "require_confirmation", "verbose", "custom_dangerous_patterns"]
        for key in required_keys:
            assert key in config
    
    def test_load_config_field_types(self):
        """Test that load_config returns correct field types."""
        config = load_config()
        
        assert isinstance(config["timeout"], int)
        assert isinstance(config["require_confirmation"], bool)
        assert isinstance(config["verbose"], bool)
        assert isinstance(config["custom_dangerous_patterns"], list)
    
    def test_load_config_consistency(self):
        """Test that load_config returns consistent results across calls."""
        config1 = load_config()
        config2 = load_config()
        
        assert config1 == config2


class TestGetDangerousPatterns:
    """Test cases for get_dangerous_patterns function."""
    
    @patch('git_gud.config.load_config')
    @patch('git_gud.safety.load_dangerous_patterns')
    def test_get_dangerous_patterns_returns_list(self, mock_load_patterns, mock_load_config):
        """Test that get_dangerous_patterns returns a list."""
        mock_load_patterns.return_value = ["pattern1", "pattern2"]
        mock_load_config.return_value = {"custom_dangerous_patterns": []}
        
        patterns = get_dangerous_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) >= 2
    
    @patch('git_gud.config.load_config')
    @patch('git_gud.safety.load_dangerous_patterns')
    def test_get_dangerous_patterns_includes_defaults(self, mock_load_patterns, mock_load_config):
        """Test that get_dangerous_patterns includes default patterns."""
        default_patterns = ["push.*force", "reset.*hard"]
        mock_load_patterns.return_value = default_patterns
        mock_load_config.return_value = {"custom_dangerous_patterns": []}
        
        patterns = get_dangerous_patterns()
        
        assert "push.*force" in patterns
        assert "reset.*hard" in patterns
    
    @patch('git_gud.config.load_config')
    @patch('git_gud.safety.load_dangerous_patterns')
    def test_get_dangerous_patterns_includes_custom(self, mock_load_patterns, mock_load_config):
        """Test that get_dangerous_patterns includes custom patterns."""
        default_patterns = ["push.*force"]
        custom_patterns = ["custom_pattern1", "custom_pattern2"]
        mock_load_patterns.return_value = default_patterns
        mock_load_config.return_value = {"custom_dangerous_patterns": custom_patterns}
        
        patterns = get_dangerous_patterns()
        
        assert "push.*force" in patterns
        assert "custom_pattern1" in patterns
        assert "custom_pattern2" in patterns
        assert len(patterns) == 3
    
    @patch('git_gud.config.load_config')
    @patch('git_gud.safety.load_dangerous_patterns')
    def test_get_dangerous_patterns_empty_custom(self, mock_load_patterns, mock_load_config):
        """Test get_dangerous_patterns with empty custom patterns."""
        default_patterns = ["push.*force", "reset.*hard"]
        mock_load_patterns.return_value = default_patterns
        mock_load_config.return_value = {"custom_dangerous_patterns": []}
        
        patterns = get_dangerous_patterns()
        
        assert patterns == default_patterns
    
    @patch('git_gud.config.load_config')
    @patch('git_gud.safety.load_dangerous_patterns')
    def test_get_dangerous_patterns_no_custom_key(self, mock_load_patterns, mock_load_config):
        """Test get_dangerous_patterns when custom_dangerous_patterns key is missing."""
        default_patterns = ["push.*force"]
        mock_load_patterns.return_value = default_patterns
        mock_load_config.return_value = {}  # Missing custom_dangerous_patterns key
        
        patterns = get_dangerous_patterns()
        
        assert patterns == default_patterns


class TestGetTimeout:
    """Test cases for get_timeout function."""
    
    @patch('git_gud.config.load_config')
    def test_get_timeout_default_value(self, mock_load_config):
        """Test get_timeout returns default value."""
        mock_load_config.return_value = {"timeout": 30}
        
        timeout = get_timeout()
        
        assert timeout == 30
        assert isinstance(timeout, int)
    
    @patch('git_gud.config.load_config')
    def test_get_timeout_custom_value(self, mock_load_config):
        """Test get_timeout returns custom value."""
        mock_load_config.return_value = {"timeout": 60}
        
        timeout = get_timeout()
        
        assert timeout == 60
    
    @patch('git_gud.config.load_config')
    def test_get_timeout_missing_key(self, mock_load_config):
        """Test get_timeout with missing timeout key."""
        mock_load_config.return_value = {}  # Missing timeout key
        
        timeout = get_timeout()
        
        assert timeout == 30  # Should return default value
    
    @patch('git_gud.config.load_config')
    def test_get_timeout_none_value(self, mock_load_config):
        """Test get_timeout with None value."""
        mock_load_config.return_value = {"timeout": None}
        
        timeout = get_timeout()
        
        assert timeout == 30  # Should return default value


class TestShouldRequireConfirmation:
    """Test cases for should_require_confirmation function."""
    
    @patch('git_gud.config.load_config')
    def test_should_require_confirmation_default_true(self, mock_load_config):
        """Test should_require_confirmation returns default True."""
        mock_load_config.return_value = {"require_confirmation": True}
        
        result = should_require_confirmation()
        
        assert result is True
        assert isinstance(result, bool)
    
    @patch('git_gud.config.load_config')
    def test_should_require_confirmation_false(self, mock_load_config):
        """Test should_require_confirmation returns False when configured."""
        mock_load_config.return_value = {"require_confirmation": False}
        
        result = should_require_confirmation()
        
        assert result is False
    
    @patch('git_gud.config.load_config')
    def test_should_require_confirmation_missing_key(self, mock_load_config):
        """Test should_require_confirmation with missing key."""
        mock_load_config.return_value = {}  # Missing require_confirmation key
        
        result = should_require_confirmation()
        
        assert result is True  # Should return default value
    
    @patch('git_gud.config.load_config')
    def test_should_require_confirmation_none_value(self, mock_load_config):
        """Test should_require_confirmation with None value."""
        mock_load_config.return_value = {"require_confirmation": None}
        
        result = should_require_confirmation()
        
        assert result is True  # Should return default value


class TestConfigErrorHandling:
    """Test cases for error handling in config module."""
    
    @patch('git_gud.safety.load_dangerous_patterns')
    def test_get_dangerous_patterns_load_config_error(self, mock_load_patterns):
        """Test get_dangerous_patterns when load_config fails."""
        mock_load_patterns.return_value = ["pattern1"]
        
        # Mock load_config to raise an exception
        with patch('git_gud.config.load_config', side_effect=Exception("Config error")):
            # Should handle the error gracefully
            patterns = get_dangerous_patterns()
            
            # Should still return the default patterns
            assert isinstance(patterns, list)
            assert "pattern1" in patterns
    
    @patch('git_gud.config.load_config')
    def test_get_dangerous_patterns_load_patterns_error(self, mock_load_config):
        """Test get_dangerous_patterns when load_dangerous_patterns fails."""
        mock_load_config.return_value = {"custom_dangerous_patterns": ["custom1"]}
        
        # Mock load_dangerous_patterns to raise an exception
        with patch('git_gud.safety.load_dangerous_patterns', side_effect=Exception("Pattern error")):
            # Should handle the error gracefully
            patterns = get_dangerous_patterns()
            
            # Should still return custom patterns if available
            assert isinstance(patterns, list)
            assert "custom1" in patterns
    
    def test_get_timeout_load_config_error(self):
        """Test get_timeout when load_config fails."""
        with patch('git_gud.config.load_config', side_effect=Exception("Config error")):
            # Should handle the error gracefully and return default
            timeout = get_timeout()
            
            assert timeout == 30
    
    def test_should_require_confirmation_load_config_error(self):
        """Test should_require_confirmation when load_config fails."""
        with patch('git_gud.config.load_config', side_effect=Exception("Config error")):
            # Should handle the error gracefully and return default
            result = should_require_confirmation()
            
            assert result is True


class TestConfigIntegration:
    """Integration tests for config module functions."""
    
    def test_config_functions_work_together(self):
        """Test that all config functions work together without mocking."""
        # Test that all functions can be called without errors
        config = load_config()
        patterns = get_dangerous_patterns()
        timeout = get_timeout()
        confirmation = should_require_confirmation()
        
        # Verify types and basic expectations
        assert isinstance(config, dict)
        assert isinstance(patterns, list)
        assert isinstance(timeout, int)
        assert isinstance(confirmation, bool)
        
        # Verify reasonable values
        assert timeout > 0
        assert len(patterns) > 0
    
    def test_config_consistency_across_calls(self):
        """Test that config functions return consistent results."""
        # Call functions multiple times
        config1 = load_config()
        config2 = load_config()
        
        timeout1 = get_timeout()
        timeout2 = get_timeout()
        
        confirmation1 = should_require_confirmation()
        confirmation2 = should_require_confirmation()
        
        # Verify consistency
        assert config1 == config2
        assert timeout1 == timeout2
        assert confirmation1 == confirmation2
    
    @patch('git_gud.config.load_config')
    def test_config_with_partial_configuration(self, mock_load_config):
        """Test config functions with partial configuration."""
        # Simulate partial config (some keys missing)
        mock_load_config.return_value = {
            "timeout": 45,
            # Missing require_confirmation and custom_dangerous_patterns
        }
        
        timeout = get_timeout()
        confirmation = should_require_confirmation()
        patterns = get_dangerous_patterns()
        
        assert timeout == 45  # Custom value
        assert confirmation is True  # Default value
        assert isinstance(patterns, list)  # Should still work
        assert len(patterns) > 0