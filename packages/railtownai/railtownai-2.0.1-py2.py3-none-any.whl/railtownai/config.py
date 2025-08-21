"""Configuration management for the Railtown AI Python SDK."""

from __future__ import annotations

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
import base64
import json


class RailtownConfig:
    """Manages Railtown AI configuration and API key parsing."""

    def __init__(self):
        self._api_key: str | None = None
        self._parsed_config: dict | None = None

    def set_api_key(self, api_key: str) -> None:
        """Set the Railtown AI API key."""
        self._api_key = api_key
        self._parsed_config = None  # Reset parsed config to force re-parsing

    def get_api_key(self) -> str | None:
        """Get the current API key."""
        return self._api_key

    def get_config(self) -> dict:
        """Get the parsed Railtown configuration from the API key."""
        if self._parsed_config is not None:
            return self._parsed_config

        try:
            if not self._api_key or self._api_key == "":
                raise Exception("Invalid Railtown AI API Key: Ensure you call init(railtown_api_key)")

            token_base64_bytes = self._api_key.encode("ascii")
            token_decoded_bytes = base64.b64decode(token_base64_bytes)
            token_json = token_decoded_bytes.decode("ascii")
            jwt = json.loads(token_json)

            # Validate required fields
            required_fields = {
                "u": "host",
                "o": "organization_id",
                "p": "project_id",
                "h": "secret",
                "e": "environment_id",
            }

            for field, name in required_fields.items():
                if field not in jwt:
                    raise Exception(f"Invalid Railtown AI API Key: {name} is required")

            self._parsed_config = jwt
            return jwt

        except Exception as e:
            raise Exception("Invalid Railtown AI API Key: Ensure to copy it from your Railtown Project") from e

    def clear(self) -> None:
        """Clear the current configuration."""
        self._api_key = None
        self._parsed_config = None


# Global configuration instance
_config = RailtownConfig()


def get_config() -> dict:
    """Get the Railtown configuration from the API key."""
    return _config.get_config()


def set_api_key(api_key: str) -> None:
    """Set the Railtown AI API key."""
    _config.set_api_key(api_key)


def get_api_key() -> str | None:
    """Get the current API key."""
    return _config.get_api_key()


def clear_config() -> None:
    """Clear the current configuration."""
    _config.clear()
