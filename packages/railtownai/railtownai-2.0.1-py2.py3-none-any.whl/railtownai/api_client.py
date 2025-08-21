"""HTTP client wrapper for Railtown AI SDK."""

from __future__ import annotations

from typing import Any

import requests


class HttpClient:
    """HTTP client wrapper for making requests to Railtown AI services."""

    def __init__(self, timeout: int = 10):
        """
        Initialize the HTTP client.

        Args:
            timeout: Default timeout in seconds for requests
        """
        self.timeout = timeout

    def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
        data: str | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """
        Make a POST request.

        Args:
            url: The URL to send the request to
            headers: Optional headers to include in the request
            json_data: Optional JSON data to send (will be serialized)
            data: Optional raw data to send
            timeout: Optional timeout override

        Returns:
            The requests.Response object

        Raises:
            requests.RequestException: If the request fails
        """
        request_timeout = timeout if timeout is not None else self.timeout

        return requests.post(
            url,
            headers=headers,
            json=json_data,
            data=data,
            timeout=request_timeout,
        )

    def put(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """
        Make a PUT request.

        Args:
            url: The URL to send the request to
            headers: Optional headers to include in the request
            data: Optional raw data to send
            timeout: Optional timeout override

        Returns:
            The requests.Response object

        Raises:
            requests.RequestException: If the request fails
        """
        request_timeout = timeout if timeout is not None else self.timeout

        return requests.put(
            url,
            headers=headers,
            data=data,
            timeout=request_timeout,
        )

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """
        Make a GET request.

        Args:
            url: The URL to send the request to
            headers: Optional headers to include in the request
            params: Optional query parameters
            timeout: Optional timeout override

        Returns:
            The requests.Response object

        Raises:
            requests.RequestException: If the request fails
        """
        request_timeout = timeout if timeout is not None else self.timeout

        return requests.get(
            url,
            headers=headers,
            params=params,
            timeout=request_timeout,
        )


# Global instance for use throughout the SDK
_http_client = HttpClient()


def get_http_client() -> HttpClient:
    """
    Get the global HTTP client instance.

    Returns:
        The global HttpClient instance
    """
    return _http_client


def set_http_client(client: HttpClient) -> None:
    """
    Set the global HTTP client instance (useful for testing).

    Args:
        client: The HttpClient instance to use globally
    """
    global _http_client
    _http_client = client
