"""Example tests for the handler module using the new HTTP client."""

from __future__ import annotations

import json
import logging
import sys
from unittest.mock import Mock

from railtownai.api_client import set_http_client
from railtownai.config import set_api_key


class TestRailtownHandlerWithHttpClient:
    """Example tests showing how to use the HTTP client instead of requests_mock."""

    def setup_method(self):
        """Set up test environment."""
        # Set a valid API key for testing
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501
        set_api_key(valid_key)

        # Store original HTTP client to restore later
        from railtownai.api_client import get_http_client

        self.original_client = get_http_client()

    def teardown_method(self):
        """Clean up test environment."""
        # Restore original HTTP client
        set_http_client(self.original_client)

    def test_emit_with_valid_config_using_http_client(self):
        """Test emit method with valid configuration using HTTP client mock."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify the HTTP client was called
        assert mock_client.post.called

        # Get the call arguments
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://test-host.com"  # URL

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "railtown-py(python)"

        # Verify payload structure
        payload = call_args[1]["json_data"]
        assert len(payload) == 1
        assert "Body" in payload[0]
        assert "UserProperties" in payload[0]

        # Verify user properties
        user_props = payload[0]["UserProperties"]
        assert user_props["AuthenticationCode"] == "test-secret"
        assert user_props["ClientVersion"].startswith("Python-")
        assert user_props["Encoding"] == "utf-8"
        assert user_props["ConnectionName"] == "test-host.com"

    def test_emit_with_exception_info_using_http_client(self):
        """Test emit method with exception information using HTTP client mock."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        try:
            raise ValueError("Test exception")
        except ValueError:
            # Create a log record with exception info
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Test error with exception",
                args=(),
                exc_info=sys.exc_info(),
            )

            handler.emit(record)

            # Verify the HTTP client was called
            assert mock_client.post.called

            # Get the payload and verify it contains exception info
            payload = mock_client.post.call_args[1]["json_data"]
            body_str = payload[0]["Body"]

            # Should contain exception information
            assert "ValueError" in body_str
            assert "Test exception" in body_str

    def test_upload_agent_run_success_using_http_client(self):
        """Test upload_agent_run method with successful upload using HTTP client mock."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the SAS URL request
        sas_response = Mock()
        sas_response.ok = True
        sas_response.text = "https://test-sas-url.com"

        # Mock the upload request
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201

        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is True

        # Verify both HTTP calls were made
        assert mock_client.post.called
        assert mock_client.put.called

        # Verify the upload request
        put_call_args = mock_client.put.call_args
        assert put_call_args[0][0] == "https://test-sas-url.com"  # URL

        # Verify headers
        headers = put_call_args[1]["headers"]
        assert headers["Content-Type"] == "text/plain; charset=utf-8"
        assert headers["x-ms-version"] == "2022-11-02"
        assert headers["x-ms-blob-type"] == "BlockBlob"

        # Verify the uploaded data matches our test data
        uploaded_data = json.loads(put_call_args[1]["data"].decode("utf-8"))
        assert uploaded_data["name"] == "test agent run"
        assert len(uploaded_data["nodes"]) == 1
        assert len(uploaded_data["steps"]) == 1
        assert len(uploaded_data["edges"]) == 1

    def test_upload_agent_run_with_http_error_using_http_client(self):
        """Test upload_agent_run method when HTTP request fails using HTTP client mock."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the SAS URL request to fail
        sas_response = Mock()
        sas_response.ok = False
        sas_response.status_code = 500
        sas_response.text = "Internal Server Error"

        mock_client.post.return_value = sas_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
        }

        result = handler.upload_agent_run(test_data)

        assert result is False
        assert mock_client.post.called
        # PUT should not be called since SAS URL request failed
        assert not mock_client.put.called

    def test_get_conductr_presigned_sas_url_success_using_http_client(self):
        """Test _get_conductr_presigned_sas_url method with successful response using HTTP client mock."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "https://test-sas-url.com"
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Set up test configuration
        test_config = {"u": "tst-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}
        handler._get_config = lambda: test_config

        result = handler._get_conductr_presigned_sas_url()

        assert result == "https://test-sas-url.com"
        assert mock_client.post.called

        # Verify the request was made correctly
        call_args = mock_client.post.call_args
        assert "testcndr.railtown.ai/api/observe/exchange" in call_args[0][0]  # URL

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "railtown-py(python)"
        assert headers["Authorization"] == "Bearer test-secret"

        # Verify payload - should contain the actual API key that was set in setup
        expected_api_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501
        assert call_args[1]["data"] == f'"{expected_api_key}"'

    def test_http_client_timeout_handling(self):
        """Test that HTTP client timeout is properly handled."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client that raises a timeout exception
        mock_client = Mock()
        mock_client.post.side_effect = Exception("Timeout")

        # Set the mock client globally
        set_http_client(mock_client)

        handler = RailtownHandler()

        # Set up test configuration
        test_config = {"u": "tst-test-host.com", "o": "test-org", "p": "test-proj", "h": "test-secret", "e": "test-env"}
        handler._get_config = lambda: test_config

        result = handler._get_conductr_presigned_sas_url()

        assert result is None
        assert mock_client.post.called
