"""Breadcrumb management for the Railtown AI Python SDK."""

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
from __future__ import annotations

import threading
from typing import Any

from .models import Breadcrumb


class BreadcrumbManager:
    """Manages breadcrumbs that are attached to log events."""

    def __init__(self, max_breadcrumbs: int = 100):
        self._breadcrumbs: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        self._max_breadcrumbs = max_breadcrumbs

    def add_breadcrumb(
        self, message: str, level: str = "info", category: str | None = None, data: dict[str, Any] | None = None
    ) -> None:
        """Add a breadcrumb that will be attached to subsequent log events."""
        breadcrumb = Breadcrumb(message, level, category, data)

        with self._lock:
            self._breadcrumbs.append(breadcrumb.to_dict())
            # Keep only the last N breadcrumbs to prevent memory issues
            if len(self._breadcrumbs) > self._max_breadcrumbs:
                self._breadcrumbs.pop(0)

    def clear_breadcrumbs(self) -> None:
        """Clear all stored breadcrumbs."""
        with self._lock:
            self._breadcrumbs.clear()

    def get_breadcrumbs(self) -> list[dict[str, Any]]:
        """Get a copy of all current breadcrumbs."""
        with self._lock:
            return self._breadcrumbs.copy()

    def set_max_breadcrumbs(self, max_breadcrumbs: int) -> None:
        """Set the maximum number of breadcrumbs to store."""
        self._max_breadcrumbs = max_breadcrumbs
        # Trim existing breadcrumbs if necessary
        with self._lock:
            while len(self._breadcrumbs) > self._max_breadcrumbs:
                self._breadcrumbs.pop(0)


# Global breadcrumb manager instance
_breadcrumb_manager = BreadcrumbManager()


def add_breadcrumb(
    message: str, level: str = "info", category: str | None = None, data: dict[str, Any] | None = None
) -> None:
    """Add a breadcrumb that will be attached to subsequent log events."""
    _breadcrumb_manager.add_breadcrumb(message, level, category, data)


def clear_breadcrumbs() -> None:
    """Clear all stored breadcrumbs."""
    _breadcrumb_manager.clear_breadcrumbs()


def get_breadcrumbs() -> list[dict[str, Any]]:
    """Get a copy of all current breadcrumbs."""
    return _breadcrumb_manager.get_breadcrumbs()


def set_max_breadcrumbs(max_breadcrumbs: int) -> None:
    """Set the maximum number of breadcrumbs to store."""
    _breadcrumb_manager.set_max_breadcrumbs(max_breadcrumbs)
