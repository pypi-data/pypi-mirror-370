#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
from __future__ import annotations

import logging
from unittest.mock import Mock

from railtownai import add_breadcrumb, clear_breadcrumbs, get_config, init
from railtownai.api_client import set_http_client


def test_get_config():
    # Test with a dummy API key that would decode to the expected values
    # This is just for testing the config parsing logic
    dummy_key = "eyJ1IjoidHN0Mzk3OGRhZGY5YTFlNDliMzgyMjI3NmRmMTU4Nzg2ZTYucmFpbHRvd25sb2dzLmNvbSIsIm8iOiJvcmciLCJwIjoicHJvaiIsImgiOiJzZWNyZXQiLCJlIjoiZW52In0="  # noqa: E501
    init(dummy_key)
    config = get_config()
    assert config["u"] == "tst3978dadf9a1e49b3822276df158786e6.railtownlogs.com"


def test_logging_handler():
    """Test the new logging handler approach."""
    # Create a mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_client.post.return_value = mock_response

    # Set the mock client globally
    set_http_client(mock_client)

    # Initialize with dummy key
    dummy_key = "eyJ1IjoidHN0Mzk3OGRhZGY5YTFlNDliMzgyMjI3NmRmMTU4Nzg2ZTYucmFpbHRvd25sb2dzLmNvbSIsIm8iOiJvcmciLCJwIjoicHJvaiIsImgiOiJzZWNyZXQiLCJlIjoiZW52In0="  # noqa: E501
    init(dummy_key)

    # Test logging through the handler
    logging.error("Test error message", extra={"foo": "bar"})
    assert mock_client.post.called


def test_breadcrumbs():
    """Test breadcrumb functionality."""
    clear_breadcrumbs()

    # Add breadcrumbs
    add_breadcrumb("Test breadcrumb 1", category="test")
    add_breadcrumb("Test breadcrumb 2", category="test", data={"key": "value"})

    # Create a mock HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_client.post.return_value = mock_response

    # Set the mock client globally
    set_http_client(mock_client)

    dummy_key = "eyJ1IjoidHN0Mzk3OGRhZGY5YTFlNDliMzgyMjI3NmRmMTU4Nzg2ZTYucmFpbHRvd25sb2dzLmNvbSIsIm8iOiJvcmciLCJwIjoicHJvaiIsImgiOiJzZWNyZXQiLCJlIjoiZW52In0="  # noqa: E501
    init(dummy_key)

    logging.error("Error with breadcrumbs")
    assert mock_client.post.called

    # Verify the request contained breadcrumbs in properties
    call_args = mock_client.post.call_args
    payload = call_args[1]["json_data"]
    assert "Breadcrumbs" in str(payload)
