"""Tests for the configuration module."""
import os
from unittest.mock import patch

from mindterm.config import Config


def test_config_initialization() -> None:
    """Test configuration initialization."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        config = Config()
        assert config.api_key == "test-key"
        # Check that base_url has a value (exact value may vary based on environment)
        assert config.base_url is not None and len(config.base_url) > 0
        # Check that model has a value (exact value may vary based on environment)
        assert config.model is not None and len(config.model) > 0


def test_config_validation() -> None:
    """Test configuration validation."""
    # Valid config
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        config = Config()
        assert config.validate() is True

    # Invalid config
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        assert config.validate() is False
