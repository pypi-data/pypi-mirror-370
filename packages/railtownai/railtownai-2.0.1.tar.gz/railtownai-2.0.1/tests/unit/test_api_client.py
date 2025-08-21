"""Tests for the API client module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from railtownai.api_client import HttpClient, get_http_client, set_http_client


class TestHttpClient:
    """Test the HttpClient class."""

    def test_http_client_initialization(self):
        """Test HttpClient initialization."""
        client = HttpClient()
        assert client.timeout == 10

        client = HttpClient(timeout=30)
        assert client.timeout == 30

    @patch("railtownai.api_client.requests.post")
    def test_post_request(self, mock_post):
        """Test POST request method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "success"
        mock_post.return_value = mock_response

        client = HttpClient()
        response = client.post(
            "https://example.com", headers={"Content-Type": "application/json"}, json_data={"key": "value"}
        )

        assert response == mock_response
        mock_post.assert_called_once_with(
            "https://example.com",
            headers={"Content-Type": "application/json"},
            json={"key": "value"},
            data=None,
            timeout=10,
        )

    @patch("railtownai.api_client.requests.put")
    def test_put_request(self, mock_put):
        """Test PUT request method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "success"
        mock_put.return_value = mock_response

        client = HttpClient()
        response = client.put("https://example.com", headers={"Content-Type": "text/plain"}, data=b"test data")

        assert response == mock_response
        mock_put.assert_called_once_with(
            "https://example.com", headers={"Content-Type": "text/plain"}, data=b"test data", timeout=10
        )

    @patch("railtownai.api_client.requests.get")
    def test_get_request(self, mock_get):
        """Test GET request method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "success"
        mock_get.return_value = mock_response

        client = HttpClient()
        response = client.get("https://example.com", headers={"Authorization": "Bearer token"}, params={"key": "value"})

        assert response == mock_response
        mock_get.assert_called_once_with(
            "https://example.com", headers={"Authorization": "Bearer token"}, params={"key": "value"}, timeout=10
        )

    def test_custom_timeout(self):
        """Test custom timeout override."""
        with patch("railtownai.api_client.requests.post") as mock_post:
            mock_response = Mock()
            mock_post.return_value = mock_response

            client = HttpClient(timeout=10)
            client.post("https://example.com", timeout=30)

            mock_post.assert_called_once()
            # Check that the custom timeout was used
            call_args = mock_post.call_args
            assert call_args[1]["timeout"] == 30


class TestHttpClientGlobal:
    """Test the global HTTP client functionality."""

    def test_get_http_client(self):
        """Test getting the global HTTP client."""
        client = get_http_client()
        assert isinstance(client, HttpClient)

    def test_set_http_client(self):
        """Test setting a custom HTTP client."""
        original_client = get_http_client()
        custom_client = HttpClient(timeout=60)

        set_http_client(custom_client)

        # Verify the global client was changed
        assert get_http_client() == custom_client
        assert get_http_client().timeout == 60

        # Restore original client
        set_http_client(original_client)
        assert get_http_client() == original_client


class TestHttpClientMocking:
    """Test how the HTTP client can be easily mocked in tests."""

    def test_mock_http_client_in_handler(self):
        """Test how the HTTP client can be mocked for handler tests."""
        from railtownai.handler import RailtownHandler

        # Create a mock HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "https://test-sas-url.com"
        mock_client.post.return_value = mock_response

        # Set the mock client globally
        set_http_client(mock_client)

        try:
            # Create a handler and test it
            handler = RailtownHandler()

            # Mock the config to return a valid configuration
            test_config = {
                "u": "tst-test-host.com",
                "o": "test-org",
                "p": "test-proj",
                "h": "test-secret",
                "e": "test-env",
            }
            handler._get_config = lambda: test_config

            # Test the method that uses HTTP client
            result = handler._get_conductr_presigned_sas_url()

            # Verify the mock was called
            assert mock_client.post.called
            assert result == "https://test-sas-url.com"

        finally:
            # Restore the original client
            from railtownai.api_client import _http_client

            set_http_client(_http_client)

    def test_mock_http_client_for_upload(self):
        """Test mocking HTTP client for upload operations."""
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

        try:
            handler = RailtownHandler()

            # Mock the config
            test_config = {
                "u": "tst-test-host.com",
                "o": "test-org",
                "p": "test-proj",
                "h": "test-secret",
                "e": "test-env",
            }
            handler._get_config = lambda: test_config

            # Test upload with valid data
            test_data = {
                "name": "test agent run",
                "session_id": "test-session-123",
                "run_id": "test-run-456",
                "nodes": [{"identifier": "node1", "node_type": "planner"}],
                "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
                "edges": [{"source": "node1", "target": "node2", "identifier": "edge1"}],
            }

            result = handler.upload_agent_run(test_data)

            # Verify both HTTP calls were made
            assert mock_client.post.called
            assert mock_client.put.called
            assert result is True

        finally:
            # Restore the original client
            from railtownai.api_client import _http_client

            set_http_client(_http_client)
