#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the models module."""

from __future__ import annotations

import datetime

from railtownai.models import Breadcrumb, RailtownPayload


class TestRailtownPayload:
    """Test the RailtownPayload model."""

    def test_railtown_payload_creation(self):
        """Test creating a RailtownPayload instance."""
        payload = RailtownPayload(
            Message="Test message",
            Level="info",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"key": "value"},
        )

        assert payload.Message == "Test message"
        assert payload.Level == "info"
        assert payload.OrganizationId == "org123"
        assert payload.ProjectId == "proj456"
        assert payload.EnvironmentId == "env789"
        assert payload.Runtime == "python-test"
        assert payload.Exception == ""
        assert payload.TimeStamp == "2023-01-01T00:00:00"
        assert payload.Properties == {"key": "value"}

    def test_railtown_payload_with_breadcrumbs(self):
        """Test RailtownPayload with breadcrumbs in properties."""
        breadcrumbs = [{"message": "test", "level": "info"}]
        payload = RailtownPayload(
            Message="Test message",
            Level="error",
            OrganizationId="org123",
            ProjectId="proj456",
            EnvironmentId="env789",
            Runtime="python-test",
            Exception="Test exception",
            TimeStamp="2023-01-01T00:00:00",
            Properties={"Breadcrumbs": breadcrumbs},
        )

        assert payload.Properties["Breadcrumbs"] == breadcrumbs
        assert len(payload.Properties["Breadcrumbs"]) == 1


class TestBreadcrumb:
    """Test the Breadcrumb class."""

    def test_breadcrumb_creation(self):
        """Test creating a basic breadcrumb."""
        breadcrumb = Breadcrumb("Test message")

        assert breadcrumb.message == "Test message"
        assert breadcrumb.level == "info"  # default
        assert breadcrumb.category is None
        assert breadcrumb.data == {}
        assert isinstance(breadcrumb.timestamp, str)

    def test_breadcrumb_with_all_parameters(self):
        """Test creating a breadcrumb with all parameters."""
        data = {"key": "value", "number": 42}
        breadcrumb = Breadcrumb(message="Test message", level="warning", category="test_category", data=data)

        assert breadcrumb.message == "Test message"
        assert breadcrumb.level == "warning"
        assert breadcrumb.category == "test_category"
        assert breadcrumb.data == data

    def test_breadcrumb_to_dict(self):
        """Test converting breadcrumb to dictionary."""
        data = {"key": "value"}
        breadcrumb = Breadcrumb(message="Test message", level="error", category="test", data=data)

        breadcrumb_dict = breadcrumb.to_dict()

        assert breadcrumb_dict["message"] == "Test message"
        assert breadcrumb_dict["level"] == "error"
        assert breadcrumb_dict["category"] == "test"
        assert breadcrumb_dict["data"] == data
        assert "timestamp" in breadcrumb_dict
        assert isinstance(breadcrumb_dict["timestamp"], str)

    def test_breadcrumb_timestamp_format(self):
        """Test that breadcrumb timestamp is in ISO format."""
        breadcrumb = Breadcrumb("Test message")

        # Verify it's a valid ISO timestamp
        datetime.datetime.fromisoformat(breadcrumb.timestamp)

        # Verify it's recent (within last minute)
        now = datetime.datetime.now()
        breadcrumb_time = datetime.datetime.fromisoformat(breadcrumb.timestamp)
        time_diff = abs((now - breadcrumb_time).total_seconds())
        assert time_diff < 60  # Should be within 60 seconds
