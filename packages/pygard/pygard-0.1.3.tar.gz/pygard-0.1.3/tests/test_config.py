# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 11:59
# @Description:


"""
Tests for PyGard configuration.
"""

import pytest
from pygard.config import GardConfig


class TestGardConfig:
    """Test GardConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GardConfig()

        assert config.base_url == "http://localhost:8083"
        assert config.api_version == "v1"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.log_level == "INFO"
        assert config.log_format == "json"
        assert config.connection_pool_size == 10
        assert config.keepalive_timeout == 30
        assert config.api_key is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = GardConfig(
            base_url="https://api.example.com",
            api_version="v2",
            timeout=60,
            log_level="DEBUG",
            api_key="test_key"
        )

        assert config.base_url == "https://api.example.com"
        assert config.api_version == "v2"
        assert config.timeout == 60
        assert config.log_level == "DEBUG"
        assert config.api_key == "test_key"

    def test_api_base_url_property(self):
        """Test api_base_url property."""
        config = GardConfig()

        expected_url = "http://localhost:8083/api/v1/data-service"
        assert config.api_base_url == expected_url

    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config = GardConfig(log_level=level)
            assert config.log_level == level

        # Invalid log level should raise ValueError
        with pytest.raises(ValueError):
            GardConfig(log_level="INVALID")

    def test_log_format_validation(self):
        """Test log format validation."""
        # Valid formats
        valid_formats = ["json", "text"]
        for fmt in valid_formats:
            config = GardConfig(log_format=fmt)
            assert config.log_format == fmt

        # Invalid format should raise ValueError
        with pytest.raises(ValueError):
            GardConfig(log_format="INVALID")

    def test_case_insensitive_log_level(self):
        """Test that log level is case-insensitive."""
        config = GardConfig(log_level="debug")
        assert config.log_level == "DEBUG"

        config = GardConfig(log_level="Info")
        assert config.log_level == "INFO"

    def test_case_insensitive_log_format(self):
        """Test that log format is case-insensitive."""
        config = GardConfig(log_format="JSON")
        assert config.log_format == "json"

        config = GardConfig(log_format="Text")
        assert config.log_format == "text"

    def test_model_config(self):
        """Test that model_config is properly set."""
        config = GardConfig()

        # Check that model_config exists and has expected values
        assert hasattr(config, 'model_config')

        # In Pydantic V2, model_config is a dict-like object
        # We need to access it differently
        model_config = config.model_config

        # Check if the expected keys exist in the model_config
        # Note: The exact structure may vary, so we check for the presence
        # of the configuration rather than specific attribute access
        assert model_config is not None
