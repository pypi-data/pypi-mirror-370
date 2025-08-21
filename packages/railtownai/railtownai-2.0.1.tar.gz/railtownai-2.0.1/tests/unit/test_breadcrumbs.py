#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the breadcrumbs module."""

from __future__ import annotations

import threading
import time

from railtownai.breadcrumbs import (
    BreadcrumbManager,
    add_breadcrumb,
    clear_breadcrumbs,
    get_breadcrumbs,
    set_max_breadcrumbs,
)


class TestBreadcrumbManager:
    """Test the BreadcrumbManager class."""

    def test_breadcrumb_manager_initialization(self):
        """Test breadcrumb manager initialization."""
        manager = BreadcrumbManager()

        assert len(manager.get_breadcrumbs()) == 0
        assert manager._max_breadcrumbs == 100

    def test_breadcrumb_manager_custom_max(self):
        """Test breadcrumb manager with custom max breadcrumbs."""
        manager = BreadcrumbManager(max_breadcrumbs=50)

        assert manager._max_breadcrumbs == 50

    def test_add_breadcrumb(self):
        """Test adding a breadcrumb."""
        manager = BreadcrumbManager()

        manager.add_breadcrumb("Test message")
        breadcrumbs = manager.get_breadcrumbs()

        assert len(breadcrumbs) == 1
        assert breadcrumbs[0]["message"] == "Test message"
        assert breadcrumbs[0]["level"] == "info"  # default
        assert breadcrumbs[0]["category"] is None
        assert breadcrumbs[0]["data"] == {}
        assert "timestamp" in breadcrumbs[0]

    def test_add_breadcrumb_with_all_parameters(self):
        """Test adding a breadcrumb with all parameters."""
        manager = BreadcrumbManager()
        data = {"key": "value", "number": 42}

        manager.add_breadcrumb(message="Test message", level="warning", category="test_category", data=data)

        breadcrumbs = manager.get_breadcrumbs()
        assert len(breadcrumbs) == 1
        assert breadcrumbs[0]["message"] == "Test message"
        assert breadcrumbs[0]["level"] == "warning"
        assert breadcrumbs[0]["category"] == "test_category"
        assert breadcrumbs[0]["data"] == data

    def test_add_multiple_breadcrumbs(self):
        """Test adding multiple breadcrumbs."""
        manager = BreadcrumbManager()

        manager.add_breadcrumb("First message")
        manager.add_breadcrumb("Second message", level="error")
        manager.add_breadcrumb("Third message", category="test")

        breadcrumbs = manager.get_breadcrumbs()
        assert len(breadcrumbs) == 3
        assert breadcrumbs[0]["message"] == "First message"
        assert breadcrumbs[1]["message"] == "Second message"
        assert breadcrumbs[1]["level"] == "error"
        assert breadcrumbs[2]["message"] == "Third message"
        assert breadcrumbs[2]["category"] == "test"

    def test_clear_breadcrumbs(self):
        """Test clearing breadcrumbs."""
        manager = BreadcrumbManager()

        manager.add_breadcrumb("Test message")
        assert len(manager.get_breadcrumbs()) == 1

        manager.clear_breadcrumbs()
        assert len(manager.get_breadcrumbs()) == 0

    def test_get_breadcrumbs_returns_copy(self):
        """Test that get_breadcrumbs returns a copy, not the original list."""
        manager = BreadcrumbManager()

        manager.add_breadcrumb("Test message")
        breadcrumbs1 = manager.get_breadcrumbs()
        breadcrumbs2 = manager.get_breadcrumbs()

        # Should be equal but not the same object
        assert breadcrumbs1 == breadcrumbs2
        assert breadcrumbs1 is not breadcrumbs2

        # Modifying the returned list shouldn't affect the manager
        breadcrumbs1.append({"message": "fake"})
        assert len(manager.get_breadcrumbs()) == 1

    def test_max_breadcrumbs_limit(self):
        """Test that breadcrumbs are limited to max_breadcrumbs."""
        manager = BreadcrumbManager(max_breadcrumbs=3)

        # Add more breadcrumbs than the limit
        for i in range(5):
            manager.add_breadcrumb(f"Message {i}")

        breadcrumbs = manager.get_breadcrumbs()
        assert len(breadcrumbs) == 3
        assert breadcrumbs[0]["message"] == "Message 2"  # First two were removed
        assert breadcrumbs[1]["message"] == "Message 3"
        assert breadcrumbs[2]["message"] == "Message 4"

    def test_set_max_breadcrumbs(self):
        """Test setting max breadcrumbs."""
        manager = BreadcrumbManager(max_breadcrumbs=5)

        # Add some breadcrumbs
        for i in range(3):
            manager.add_breadcrumb(f"Message {i}")

        # Reduce max breadcrumbs
        manager.set_max_breadcrumbs(2)
        breadcrumbs = manager.get_breadcrumbs()
        assert len(breadcrumbs) == 2
        assert breadcrumbs[0]["message"] == "Message 1"
        assert breadcrumbs[1]["message"] == "Message 2"

    def test_thread_safety(self):
        """Test that breadcrumb manager is thread-safe."""
        manager = BreadcrumbManager()
        results = []  # noqa: F841

        def add_breadcrumbs():
            for i in range(10):
                manager.add_breadcrumb(f"Thread message {i}")
                time.sleep(0.001)  # Small delay to increase race condition chance

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=add_breadcrumbs)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have exactly 50 breadcrumbs (5 threads * 10 breadcrumbs each)
        breadcrumbs = manager.get_breadcrumbs()
        assert len(breadcrumbs) == 50


class TestBreadcrumbFunctions:
    """Test the module-level breadcrumb functions."""

    def setup_method(self):
        """Clear breadcrumbs before each test."""
        clear_breadcrumbs()

    def test_add_breadcrumb_function(self):
        """Test add_breadcrumb function."""
        add_breadcrumb("Test message", level="warning", category="test")

        breadcrumbs = get_breadcrumbs()
        assert len(breadcrumbs) == 1
        assert breadcrumbs[0]["message"] == "Test message"
        assert breadcrumbs[0]["level"] == "warning"
        assert breadcrumbs[0]["category"] == "test"

    def test_clear_breadcrumbs_function(self):
        """Test clear_breadcrumbs function."""
        add_breadcrumb("Test message")
        assert len(get_breadcrumbs()) == 1

        clear_breadcrumbs()
        assert len(get_breadcrumbs()) == 0

    def test_get_breadcrumbs_function(self):
        """Test get_breadcrumbs function."""
        add_breadcrumb("First message")
        add_breadcrumb("Second message")

        breadcrumbs = get_breadcrumbs()
        assert len(breadcrumbs) == 2
        assert breadcrumbs[0]["message"] == "First message"
        assert breadcrumbs[1]["message"] == "Second message"

    def test_set_max_breadcrumbs_function(self):
        """Test set_max_breadcrumbs function."""
        set_max_breadcrumbs(2)

        add_breadcrumb("First message")
        add_breadcrumb("Second message")
        add_breadcrumb("Third message")  # Should cause first to be removed

        breadcrumbs = get_breadcrumbs()
        assert len(breadcrumbs) == 2
        assert breadcrumbs[0]["message"] == "Second message"
        assert breadcrumbs[1]["message"] == "Third message"
