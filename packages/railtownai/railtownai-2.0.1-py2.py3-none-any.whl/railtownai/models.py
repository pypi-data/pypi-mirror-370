"""Data models for the Railtown AI Python SDK."""

from __future__ import annotations

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
import datetime
from typing import Any

from pydantic import BaseModel


class RailtownPayload(BaseModel):
    """Payload model for sending data to Railtown AI."""

    Message: str
    Level: str
    OrganizationId: str
    ProjectId: str
    EnvironmentId: str
    Runtime: str
    Exception: str
    TimeStamp: str
    Properties: dict


class Breadcrumb:
    """Represents a breadcrumb that can be attached to log events."""

    def __init__(
        self,
        message: str,
        level: str = "info",
        category: str | None = None,
        data: dict[str, Any] | None = None,
    ):
        self.message = message
        self.level = level
        self.category = category
        self.data = data or {}
        self.timestamp = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert breadcrumb to dictionary representation."""
        return {
            "message": self.message,
            "level": self.level,
            "category": self.category,
            "data": self.data,
            "timestamp": self.timestamp,
        }
