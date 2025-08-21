"""Core functionality for the Railtown AI Python SDK."""

from __future__ import annotations

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
import logging
from typing import Any

from .config import set_api_key
from .handler import RailtownHandler


def init(token: str) -> None:
    """Initialize Railtown AI with your API key."""
    # Set the API key
    set_api_key(token)

    # Add the Railtown handler to the root logger
    root_logger = logging.getLogger()

    # Remove any existing Railtown handlers
    for handler in root_logger.handlers[:]:
        if isinstance(handler, RailtownHandler):
            root_logger.removeHandler(handler)

    # Add new Railtown handler
    railtown_handler = RailtownHandler()
    railtown_handler.setLevel(logging.INFO)  # Default to INFO level
    root_logger.addHandler(railtown_handler)

    # Set root logger level to INFO to capture all relevant logs
    if root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)


def get_railtown_handler() -> RailtownHandler | None:
    """
    Get the Railtown AI handler from the root logger.

    Ensures only one RailtownHandler exists. If multiple handlers are found,
    raises a RuntimeError as this indicates an inconsistent state.

    Returns:
        RailtownHandler | None: The Railtown handler if found, None otherwise

    Raises:
        RuntimeError: If multiple RailtownHandler instances are found

    Example:
        >>> rt_logger = get_railtown_handler()
        >>> if rt_logger:
        ...     rt_logger.upload_agent_run(serialized_agent_run_json)
    """
    root_logger = logging.getLogger()

    railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]

    if len(railtown_handlers) > 1:
        raise RuntimeError(
            f"Multiple RailtownHandler instances found ({len(railtown_handlers)}). "
            "This indicates an inconsistent state. Only one handler should exist."
        )

    return railtown_handlers[0] if railtown_handlers else None


def upload_agent_run(payloads: dict[str, Any] | list[dict[str, Any]]) -> bool:
    """
    Upload agent run data to Railtown AI.

    This is a convenience function that delegates to the RailtownHandler.
    You must call railtownai.init() before using this function.

    Args:
        payloads: Either a single JSON object or a list of JSON objects to save

    Returns:
        bool: True if all uploads succeed, False if any upload fails

    Raises:
        RuntimeError: If no RailtownHandler is found (railtownai.init() not called)

    Example:
        >>> railtownai.init("YOUR_API_KEY")
        >>> agent_run_data = {
        ...     "name": "my_agent_run",
        ...     "nodes": [{"identifier": "node1", "node_type": "planner"}],
        ...     "steps": [{"step": 1, "time": 1234567890, "identifier": "step1"}],
        ...     "edges": [{"source": "node1", "target": "node2", "identifier": "edge1", "details": {}}],
        ... }
        >>> success = railtownai.upload_agent_run(agent_run_data)
    """
    handler = get_railtown_handler()
    if not handler:
        raise RuntimeError("No RailtownHandler found. Please call railtownai.init() first.")
    return handler.upload_agent_run(payloads)
