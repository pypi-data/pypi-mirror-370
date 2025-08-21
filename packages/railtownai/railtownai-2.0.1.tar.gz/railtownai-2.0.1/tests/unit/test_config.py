#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the config module."""

from __future__ import annotations

import pytest

from railtownai.config import (
    RailtownConfig,
    clear_config,
    get_api_key,
    get_config,
    set_api_key,
)


class TestRailtownConfig:
    """Test the RailtownConfig class."""

    def test_config_initialization(self):
        """Test config initialization."""
        config = RailtownConfig()

        assert config.get_api_key() is None
        assert config._parsed_config is None

    def test_set_api_key(self):
        """Test setting API key."""
        config = RailtownConfig()
        test_key = "test_api_key"

        config.set_api_key(test_key)
        assert config.get_api_key() == test_key
        assert config._parsed_config is None  # Should reset parsed config

    def test_get_config_with_valid_key(self):
        """Test getting config with a valid API key."""
        config = RailtownConfig()

        # Valid base64 encoded JWT with all required fields
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501
        config.set_api_key(valid_key)

        result = config.get_config()

        assert result["u"] == "test-host.com"
        assert result["o"] == "test-org"
        assert result["p"] == "test-proj"
        assert result["h"] == "test-secret"
        assert result["e"] == "test-env"

        # Test caching - should return same result without re-parsing
        cached_result = config.get_config()
        assert cached_result == result

    def test_get_config_with_missing_field(self):
        """Test getting config with missing required field."""
        config = RailtownConfig()

        # JWT missing the 'e' field
        invalid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQifQ=="  # noqa: E501
        config.set_api_key(invalid_key)

        with pytest.raises(
            Exception,
            match="Invalid Railtown AI API Key: Ensure to copy it from your Railtown Project",  # noqa: E501
        ):
            config.get_config()

    def test_get_config_with_empty_key(self):
        """Test getting config with empty API key."""
        config = RailtownConfig()
        config.set_api_key("")

        with pytest.raises(Exception, match="Invalid Railtown AI API Key"):
            config.get_config()

    def test_get_config_with_none_key(self):
        """Test getting config with None API key."""
        config = RailtownConfig()

        with pytest.raises(Exception, match="Invalid Railtown AI API Key"):
            config.get_config()

    def test_get_config_with_invalid_base64(self):
        """Test getting config with invalid base64."""
        config = RailtownConfig()
        config.set_api_key("invalid_base64!")

        with pytest.raises(Exception, match="Invalid Railtown AI API Key"):
            config.get_config()

    def test_get_config_with_invalid_json(self):
        """Test getting config with invalid JSON in base64."""
        config = RailtownConfig()
        import base64

        invalid_json = base64.b64encode(b"invalid json").decode("ascii")
        config.set_api_key(invalid_json)

        with pytest.raises(Exception, match="Invalid Railtown AI API Key"):
            config.get_config()

    def test_clear_config(self):
        """Test clearing configuration."""
        config = RailtownConfig()

        # Use a valid key for this test
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501
        config.set_api_key(valid_key)
        config.get_config()  # This should cache the parsed config

        config.clear()

        assert config.get_api_key() is None
        assert config._parsed_config is None


class TestConfigFunctions:
    """Test the module-level config functions."""

    def setup_method(self):
        """Clear config before each test."""
        clear_config()

    def test_set_and_get_api_key(self):
        """Test setting and getting API key through module functions."""
        test_key = "test_api_key"

        set_api_key(test_key)
        assert get_api_key() == test_key

    def test_get_config_function(self):
        """Test get_config function with valid key."""
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501

        set_api_key(valid_key)
        config = get_config()

        assert config["u"] == "test-host.com"
        assert config["o"] == "test-org"
        assert config["p"] == "test-proj"
        assert config["h"] == "test-secret"
        assert config["e"] == "test-env"

    def test_clear_config_function(self):
        """Test clear_config function."""
        test_key = "test_api_key"
        set_api_key(test_key)

        clear_config()
        assert get_api_key() is None

        with pytest.raises(Exception, match="Invalid Railtown AI API Key"):
            get_config()
