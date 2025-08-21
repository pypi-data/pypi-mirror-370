#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the core module."""

from __future__ import annotations

import logging
from unittest.mock import Mock

import pytest

from railtownai.config import clear_config, get_api_key
from railtownai.core import get_railtown_handler, init, upload_agent_run
from railtownai.handler import RailtownHandler


class TestCoreFunctions:
    """Test core functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any existing configuration
        clear_config()

        # Remove any existing Railtown handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

    def teardown_method(self):
        """Clean up after each test."""
        # Clear configuration
        clear_config()

        # Remove any Railtown handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

    def test_init_function(self):
        """Test the init function."""
        test_token = "test_api_key"

        # Initialize Railtown
        init(test_token)

        # Verify API key was set
        assert get_api_key() == test_token

        # Verify handler was added to root logger
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

        # Verify handler level is set to INFO
        handler = railtown_handlers[0]
        assert handler.level == logging.INFO

    def test_init_function_replaces_existing_handler(self):
        """Test that init function replaces existing Railtown handlers."""
        test_token1 = "test_api_key_1"
        test_token2 = "test_api_key_2"

        # Initialize with first token
        init(test_token1)

        # Get the first handler
        root_logger = logging.getLogger()
        handlers_before = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(handlers_before) == 1
        first_handler = handlers_before[0]

        # Initialize with second token
        init(test_token2)

        # Verify API key was updated
        assert get_api_key() == test_token2

        # Verify handler was replaced (should still be only one)
        handlers_after = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(handlers_after) == 1

        # Verify it's a different handler object
        second_handler = handlers_after[0]
        assert first_handler is not second_handler

    def test_init_function_sets_root_logger_level(self):
        """Test that init function sets root logger level appropriately."""
        # Set root logger to a high level
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.CRITICAL)

        test_token = "test_api_key"
        init(test_token)

        # Should set root logger to INFO if it was higher
        assert root_logger.level == logging.INFO

    def test_init_function_preserves_root_logger_level(self):
        """Test that init function preserves root logger level if already low enough."""
        # Set root logger to DEBUG (lower than INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        test_token = "test_api_key"
        init(test_token)

        # Should preserve the DEBUG level
        assert root_logger.level == logging.DEBUG

    def test_init_function_with_valid_api_key(self):
        """Test init function with a valid API key."""
        # Valid base64 encoded JWT
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501

        init(valid_key)

        # Verify API key was set
        assert get_api_key() == valid_key

        # Verify handler was added
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

    def test_init_function_with_empty_token(self):
        """Test init function with empty token."""
        init("")

        # Should still set the empty token
        assert get_api_key() == ""

        # Should still add handler (validation happens later)
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

    def test_init_function_multiple_calls(self):
        """Test multiple calls to init function."""
        test_token1 = "test_api_key_1"
        test_token2 = "test_api_key_2"
        test_token3 = "test_api_key_3"

        # Multiple init calls
        init(test_token1)
        init(test_token2)
        init(test_token3)

        # Should use the last token
        assert get_api_key() == test_token3

        # Should have only one handler
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

    def test_get_railtown_handler_with_handler_present(self):
        """Test get_railtown_handler when a RailtownHandler is present."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return a RailtownHandler instance
        assert handler is not None
        assert isinstance(handler, RailtownHandler)
        assert handler.level == logging.INFO

    def test_get_railtown_handler_without_handler(self):
        """Test get_railtown_handler when no RailtownHandler is present."""
        # Ensure no Railtown handlers exist
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return None when no handler is present
        assert handler is None

    def test_get_railtown_handler_with_multiple_handlers(self):
        """Test get_railtown_handler when multiple handlers exist but only one is RailtownHandler."""
        # Add a non-Railtown handler first
        root_logger = logging.getLogger()
        console_handler = logging.StreamHandler()
        root_logger.addHandler(console_handler)

        # Initialize Railtown to add a RailtownHandler
        test_token = "test_api_key"
        init(test_token)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return the RailtownHandler instance
        assert handler is not None
        assert isinstance(handler, RailtownHandler)

        # Verify other handlers are still present
        all_handlers = root_logger.handlers
        assert len(all_handlers) >= 2  # At least console handler + railtown handler

        # Clean up
        root_logger.removeHandler(console_handler)

    def test_get_railtown_handler_returns_first_handler(self):
        """Test that get_railtown_handler returns the first RailtownHandler found."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return the same handler that was added by init
        root_logger = logging.getLogger()
        railtown_handlers = [h for h in root_logger.handlers if isinstance(h, RailtownHandler)]
        assert len(railtown_handlers) == 1
        assert handler is railtown_handlers[0]

    def test_get_railtown_handler_after_handler_removal(self):
        """Test get_railtown_handler after the handler has been removed."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Verify handler is present
        handler = get_railtown_handler()
        assert handler is not None

        # Remove the handler manually
        root_logger = logging.getLogger()
        root_logger.removeHandler(handler)

        # Verify handler is no longer found
        handler_after_removal = get_railtown_handler()
        assert handler_after_removal is None

    def test_get_railtown_handler_after_reinitialization(self):
        """Test get_railtown_handler after reinitializing with a new token."""
        # Initialize with first token
        test_token1 = "test_api_key_1"
        init(test_token1)

        # Get the first handler
        handler1 = get_railtown_handler()
        assert handler1 is not None

        # Initialize with second token (should replace handler)
        test_token2 = "test_api_key_2"
        init(test_token2)

        # Get the new handler
        handler2 = get_railtown_handler()
        assert handler2 is not None

        # Should be different handler objects
        assert handler1 is not handler2

        # Both should be RailtownHandler instances
        assert isinstance(handler1, RailtownHandler)
        assert isinstance(handler2, RailtownHandler)

    def test_get_railtown_handler_with_multiple_railtown_handlers(self):
        """Test get_railtown_handler raises RuntimeError when multiple RailtownHandler instances exist."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Manually add another RailtownHandler (this shouldn't happen in normal usage)
        root_logger = logging.getLogger()
        second_handler = RailtownHandler()
        root_logger.addHandler(second_handler)

        # Verify we now have multiple RailtownHandler instances
        railtown_handlers = [h for h in root_logger.handlers if isinstance(h, RailtownHandler)]
        assert len(railtown_handlers) == 2

        # Should raise RuntimeError when multiple handlers exist
        with pytest.raises(RuntimeError) as exc_info:
            get_railtown_handler()

        # Verify the error message
        assert "Multiple RailtownHandler instances found" in str(exc_info.value)
        assert "2" in str(exc_info.value)  # Should mention the count
        assert "Only one handler should exist" in str(exc_info.value)

        # Clean up the extra handler
        root_logger.removeHandler(second_handler)

    def test_upload_agent_run_success_with_single_payload(self):
        """Test upload_agent_run with successful single payload upload."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        from railtownai.api_client import set_http_client
        set_http_client(mock_client)

        # Initialize Railtown
        init("test_api_key")

        # Mock the _get_conductr_presigned_sas_url method
        handler = get_railtown_handler()
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = upload_agent_run(test_data)

        assert result is True
        assert mock_client.put.called

    def test_upload_agent_run_success_with_array_payloads(self):
        """Test upload_agent_run with successful array of payloads upload."""
        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_client.put.return_value = mock_response

        # Set the mock client globally
        from railtownai.api_client import set_http_client
        set_http_client(mock_client)

        # Initialize Railtown
        init("test_api_key")

        # Mock the _get_conductr_presigned_sas_url method
        handler = get_railtown_handler()
        handler._get_conductr_presigned_sas_url = lambda: "https://test-sas-url.com"

        test_data_array = [
            {
                "name": "test agent run 1",
                "session_id": "test-session-123",
                "run_id": "test-run-456",
                "nodes": [{"identifier": "node1", "node_type": "planner"}],
                "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
                "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
            },
            {
                "name": "test agent run 2",
                "session_id": "test-session-124",
                "run_id": "test-run-457",
                "nodes": [{"identifier": "node2", "node_type": "executor"}],
                "steps": [{"step": 2, "time": 1234567891, "identifier": "step2"}],
                "edges": [{"source": "node2", "target": "node3", "identifier": "edge2", "details": {}}],
            },
        ]

        result = upload_agent_run(test_data_array)

        assert result is True
        assert mock_client.put.call_count == 2  # Should be called twice for two payloads

    def test_upload_agent_run_no_handler_found(self):
        """Test upload_agent_run when no handler exists (railtownai.init() not called)."""
        # Ensure no Railtown handlers exist
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

        test_data = {
            "name": "test agent run",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        with pytest.raises(RuntimeError) as exc_info:
            upload_agent_run(test_data)

        assert "No RailtownHandler found" in str(exc_info.value)
        assert "railtownai.init()" in str(exc_info.value)

    def test_upload_agent_run_delegates_to_handler(self):
        """Test that upload_agent_run properly delegates to the handler method."""
        # Initialize Railtown
        init("test_api_key")

        # Get the handler and mock its upload_agent_run method
        handler = get_railtown_handler()
        handler.upload_agent_run = Mock(return_value=True)

        test_data = {
            "name": "test agent run",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = upload_agent_run(test_data)

        # Verify the handler method was called with the correct data
        handler.upload_agent_run.assert_called_once_with(test_data)
        assert result is True

    def test_upload_agent_run_returns_handler_result(self):
        """Test that upload_agent_run returns the same result as the handler method."""
        # Initialize Railtown
        init("test_api_key")

        # Get the handler and mock its upload_agent_run method to return False
        handler = get_railtown_handler()
        handler.upload_agent_run = Mock(return_value=False)

        test_data = {
            "name": "test agent run",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = upload_agent_run(test_data)

        # Verify the result matches the handler's return value
        assert result is False

    def test_upload_agent_run_with_multiple_handlers_error(self):
        """Test upload_agent_run when multiple RailtownHandler instances exist."""
        # Initialize Railtown to add a handler
        init("test_api_key")

        # Manually add another RailtownHandler (this shouldn't happen in normal usage)
        root_logger = logging.getLogger()
        second_handler = RailtownHandler()
        root_logger.addHandler(second_handler)

        test_data = {
            "name": "test agent run",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        # Should raise RuntimeError when multiple handlers exist
        with pytest.raises(RuntimeError) as exc_info:
            upload_agent_run(test_data)

        assert "Multiple RailtownHandler instances found" in str(exc_info.value)

        # Clean up the extra handler
        root_logger.removeHandler(second_handler)
