#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the conductr integration functionality."""

from __future__ import annotations

import json
from unittest.mock import Mock

from railtownai.api_client import set_http_client
from railtownai.config import set_api_key
from railtownai.handler import RailtownHandler


class TestConductrIntegration:
    """Test the conductr integration methods in RailtownHandler."""

    def setup_method(self):
        """Set up test environment."""
        # Set a valid API key for testing with tst prefix for test environment
        valid_key = "eyJ1IjoidHN0LXRlc3QtaG9zdC5jb20iLCJvIjoidGVzdC1vcmciLCJwIjoidGVzdC1wcm9qIiwiaCI6InRlc3Qtc2VjcmV0IiwiZSI6InRlc3QtZW52In0="  # noqa: E501
        set_api_key(valid_key)

        # Store original HTTP client to restore later
        from railtownai.api_client import get_http_client

        self.original_client = get_http_client()

    def teardown_method(self):
        """Clean up test environment."""
        # Restore original HTTP client
        set_http_client(self.original_client)

    def test_get_conductr_presigned_sas_url_success(self):
        """Test _get_conductr_presigned_sas_url method with successful response."""
        handler = RailtownHandler()

        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler._get_conductr_presigned_sas_url()

        # Verify result
        assert result == "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Verify request was made correctly
        assert mock_client.post.called
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://testcndr.railtown.ai/api/observe/exchange"  # URL

        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "railtown-py(python)"
        assert headers["Authorization"] == "Bearer test-secret"

        # Verify request body
        # The payload should be the API key with encapsulating double quotes
        expected_api_key = "eyJ1IjoidHN0LXRlc3QtaG9zdC5jb20iLCJvIjoidGVzdC1vcmciLCJwIjoidGVzdC1wcm9qIiwiaCI6InRlc3Qtc2VjcmV0IiwiZSI6InRlc3QtZW52In0="  # noqa: E501
        expected_payload = f'"{expected_api_key}"'
        assert call_args[1]["data"] == expected_payload

    def test_get_conductr_presigned_sas_url_no_config(self):
        """Test _get_conductr_presigned_sas_url method when no configuration is available."""
        handler = RailtownHandler()

        # Clear the API key to simulate no configuration
        from railtownai.config import clear_config

        clear_config()

        result = handler._get_conductr_presigned_sas_url()
        assert result is None

    def test_get_conductr_presigned_sas_url_http_error(self):
        """Test _get_conductr_presigned_sas_url method when HTTP request fails."""
        handler = RailtownHandler()

        # Create a mock HTTP client that returns an error
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler._get_conductr_presigned_sas_url()
        assert result is None

    def test_get_conductr_presigned_sas_url_no_url_in_response(self):
        """Test _get_conductr_presigned_sas_url method when response doesn't contain URL."""
        handler = RailtownHandler()

        # Create a mock HTTP client that returns JSON instead of URL
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler._get_conductr_presigned_sas_url()
        # The handler returns the response text regardless of content when status is 200
        assert result == '{"status": "success"}'

    def test_upload_agent_run_success(self):
        """Test upload_agent_run method with successful upload."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL request
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload request
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201
        upload_response.text = ""

        # Set up the mock to return different responses for different calls
        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data)

        # Verify result
        assert result is True

        # Verify both requests were made
        assert mock_client.post.call_count == 1
        assert mock_client.put.call_count == 1

        # Verify the PUT request was made with correct data
        put_call_args = mock_client.put.call_args
        assert put_call_args[0][0] == "https://storage.blob.core.windows.net/container/blob?sas_token"  # URL

        # Verify headers
        headers = put_call_args[1]["headers"]
        assert headers["Content-Type"] == "text/plain; charset=utf-8"
        assert headers["x-ms-version"] == "2022-11-02"
        assert headers["x-ms-blob-type"] == "BlockBlob"

        # Verify data was JSON serialized
        data = put_call_args[1]["data"]
        assert isinstance(data, bytes)
        json_data = json.loads(data.decode("utf-8"))
        assert json_data == test_data

    def test_upload_agent_run_no_sas_url(self):
        """Test upload_agent_run method when no SAS URL is returned."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "key": "value",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        # Create a mock HTTP client that returns no URL
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = ""
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data)

        # Verify result
        assert result is False

    def test_upload_agent_run_upload_failure(self):
        """Test upload_agent_run method when blob upload fails."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "key": "value",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL request
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload request to fail
        upload_response = Mock()
        upload_response.ok = False
        upload_response.status_code = 500
        upload_response.text = "Upload failed"

        # Set up the mock to return different responses for different calls
        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data)

        # Verify result
        assert result is False

    def test_upload_agent_run_with_complex_data(self):
        """Test upload_agent_run method with complex nested data."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "string": "test",
            "number": 123,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"},
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL request
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload request
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 200
        upload_response.text = ""

        # Set up the mock to return different responses for different calls
        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data)

        # Verify result
        assert result is True

        # Verify both requests were made
        assert mock_client.post.call_count == 1
        assert mock_client.put.call_count == 1

        # Verify the PUT request was made with correct data
        put_call_args = mock_client.put.call_args
        assert put_call_args[0][0] == "https://storage.blob.core.windows.net/container/blob?sas_token"  # URL

        # Verify data was JSON serialized correctly
        data = put_call_args[1]["data"]
        assert isinstance(data, bytes)
        json_data = json.loads(data.decode("utf-8"))
        assert json_data == test_data

    # ============================================================================
    # Tests for new array functionality
    # ============================================================================

    def test_upload_agent_run_array_success(self):
        """Test upload_agent_run method with array of valid payloads."""
        handler = RailtownHandler()

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

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL requests (one for each payload)
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload requests (one for each payload)
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201
        upload_response.text = ""

        # Set up the mock to return different responses for different calls
        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data_array)

        # Verify result
        assert result is True

        # Verify both requests were made for each payload (2 payloads = 4 total calls)
        assert mock_client.post.call_count == 2  # One SAS URL request per payload
        assert mock_client.put.call_count == 2  # One upload per payload

        # Verify the PUT requests were made with correct data
        put_calls = mock_client.put.call_args_list
        assert len(put_calls) == 2

        for i, put_call in enumerate(put_calls):
            assert put_call[0][0] == "https://storage.blob.core.windows.net/container/blob?sas_token"

            # Verify data was JSON serialized correctly for each payload
            data = put_call[1]["data"]
            assert isinstance(data, bytes)
            json_data = json.loads(data.decode("utf-8"))
            assert json_data == test_data_array[i]

    def test_upload_agent_run_array_partial_failure(self):
        """Test upload_agent_run method with array where some payloads fail."""
        handler = RailtownHandler()

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

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL requests (both succeed)
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload requests (first succeeds, second fails)
        def mock_put(*args, **kwargs):
            response = Mock()
            # Make the second call fail
            if mock_client.put.call_count == 0:
                response.ok = True
                response.status_code = 201
            else:
                response.ok = False
                response.status_code = 500
                response.text = "Upload failed"
            return response

        mock_client.post.return_value = sas_response
        mock_client.put.side_effect = mock_put

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be False because one upload failed
        assert result is False

        # Verify both requests were made for each payload
        assert mock_client.post.call_count == 2
        assert mock_client.put.call_count == 2

    def test_upload_agent_run_array_all_failures(self):
        """Test upload_agent_run method with array where all payloads fail."""
        handler = RailtownHandler()

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

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL requests (both succeed)
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload requests (both fail)
        upload_response = Mock()
        upload_response.ok = False
        upload_response.status_code = 500
        upload_response.text = "Upload failed"

        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be False because all uploads failed
        assert result is False

        # Verify both requests were made for each payload
        assert mock_client.post.call_count == 2
        assert mock_client.put.call_count == 2

    def test_upload_agent_run_array_sas_url_failures(self):
        """Test upload_agent_run method with array where some SAS URL requests fail."""
        handler = RailtownHandler()

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

        # Create a mock HTTP client
        mock_client = Mock()

        # Track call count manually
        call_count = 0

        # Mock the presigned SAS URL requests (first succeeds, second fails)
        def mock_post(*args, **kwargs):
            nonlocal call_count
            response = Mock()
            # Make the second call fail
            if call_count == 0:
                response.ok = True
                response.status_code = 200
                response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"
            else:
                response.ok = False
                response.status_code = 500
                response.text = "SAS URL request failed"
            call_count += 1
            return response

        # Mock the blob upload request (only called for first payload)
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201
        upload_response.text = ""

        mock_client.post.side_effect = mock_post
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be False because second SAS URL request failed
        assert result is False

        # Verify SAS URL requests were made for both payloads
        assert mock_client.post.call_count == 2
        # Verify only one upload was attempted (for the first payload)
        assert mock_client.put.call_count == 1

    def test_upload_agent_run_array_invalid_payloads(self):
        """Test upload_agent_run method with array containing invalid payloads."""
        handler = RailtownHandler()

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
                "nodes": [],  # Invalid: empty nodes
                "steps": [{"step": 2, "time": 1234567891, "identifier": "step2"}],
                "edges": [{"source": "node2", "target": "node3", "identifier": "edge2", "details": {}}],
            },
        ]

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL request (only called for first payload)
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload request (only called for first payload)
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201
        upload_response.text = ""

        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be False because second payload is invalid
        assert result is False

        # Verify SAS URL request was made only for first payload
        assert mock_client.post.call_count == 1
        # Verify upload was attempted only for first payload
        assert mock_client.put.call_count == 1

    def test_upload_agent_run_array_empty_list(self):
        """Test upload_agent_run method with empty array."""
        handler = RailtownHandler()

        test_data_array = []

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be True for empty array
        assert result is True

    def test_upload_agent_run_array_invalid_input_type(self):
        """Test upload_agent_run method with invalid input type."""
        handler = RailtownHandler()

        # Test with string instead of dict or list
        invalid_input = "not a dict or list"

        result = handler.upload_agent_run(invalid_input)

        # Verify result - should be False for invalid input
        assert result is False

    def test_upload_agent_run_array_mixed_types(self):
        """Test upload_agent_run method with array containing non-dict items."""
        handler = RailtownHandler()

        test_data_array = [
            {
                "name": "test agent run 1",
                "session_id": "test-session-123",
                "run_id": "test-run-456",
                "nodes": [{"identifier": "node1", "node_type": "planner"}],
                "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
                "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
            },
            "not a dict",  # Invalid item
        ]

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be False for invalid input
        assert result is False

    def test_upload_agent_run_backward_compatibility(self):
        """Test that upload_agent_run maintains backward compatibility with single dict."""
        handler = RailtownHandler()

        test_data = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL request
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload request
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201
        upload_response.text = ""

        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data)

        # Verify result
        assert result is True

        # Verify both requests were made exactly once (same as before)
        assert mock_client.post.call_count == 1
        assert mock_client.put.call_count == 1

        # Verify the PUT request was made with correct data
        put_call_args = mock_client.put.call_args
        assert put_call_args[0][0] == "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Verify data was JSON serialized correctly
        data = put_call_args[1]["data"]
        assert isinstance(data, bytes)
        json_data = json.loads(data.decode("utf-8"))
        assert json_data == test_data

    def test_upload_agent_run_missing_required_fields(self):
        """Test upload_agent_run method with missing required fields."""
        handler = RailtownHandler()

        # Test data missing name
        test_data_missing_name = {
            "session_id": "test-session-123",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data_missing_name)
        assert result is False

        # Test data missing session_id
        test_data_missing_session_id = {
            "name": "test agent run",
            "run_id": "test-run-456",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data_missing_session_id)
        assert result is False

        # Test data missing run_id
        test_data_missing_run_id = {
            "name": "test agent run",
            "session_id": "test-session-123",
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data_missing_run_id)
        assert result is False

        # Test data missing multiple required fields
        test_data_missing_multiple = {
            "nodes": [{"identifier": "node1", "node_type": "planner"}],
            "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
            "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        }

        result = handler.upload_agent_run(test_data_missing_multiple)
        assert result is False

    def test_upload_agent_run_array_missing_required_fields(self):
        """Test upload_agent_run method with array containing payloads missing required fields."""
        handler = RailtownHandler()

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
                # Missing session_id and run_id
                "nodes": [{"identifier": "node2", "node_type": "executor"}],
                "steps": [{"step": 2, "time": 1234567891, "identifier": "step2"}],
                "edges": [{"source": "node2", "target": "node3", "identifier": "edge2", "details": {}}],
            },
        ]

        # Create a mock HTTP client
        mock_client = Mock()

        # Mock the presigned SAS URL request (only called for first payload)
        sas_response = Mock()
        sas_response.ok = True
        sas_response.status_code = 200
        sas_response.text = "https://storage.blob.core.windows.net/container/blob?sas_token"

        # Mock the blob upload request (only called for first payload)
        upload_response = Mock()
        upload_response.ok = True
        upload_response.status_code = 201
        upload_response.text = ""

        mock_client.post.return_value = sas_response
        mock_client.put.return_value = upload_response

        # Set the mock client globally
        set_http_client(mock_client)

        result = handler.upload_agent_run(test_data_array)

        # Verify result - should be False because second payload is missing required fields
        assert result is False

        # Verify SAS URL request was made only for first payload
        assert mock_client.post.call_count == 1
        # Verify upload was attempted only for first payload
        assert mock_client.put.call_count == 1
