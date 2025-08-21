"""Railtown AI Python SDK for tracking errors and exceptions in your Python applications"""

from __future__ import annotations

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
from dotenv import load_dotenv

from .breadcrumbs import BreadcrumbManager, add_breadcrumb, clear_breadcrumbs, get_breadcrumbs, set_max_breadcrumbs
from .config import RailtownConfig, clear_config, get_api_key, get_config, set_api_key
from .core import get_railtown_handler, init, upload_agent_run
from .handler import RailtownHandler

# Import classes for advanced usage
from .models import Breadcrumb, RailtownPayload

load_dotenv()

# VERSION - must be defined here for Flit to detect it
__version__ = "2.0.1"


# Public API
__all__ = [
    # Core functions
    "init",
    "get_railtown_handler",
    "upload_agent_run",
    "get_config",
    "set_api_key",
    "get_api_key",
    "clear_config",
    # Breadcrumb functions
    "add_breadcrumb",
    "clear_breadcrumbs",
    "get_breadcrumbs",
    "set_max_breadcrumbs",
    # Classes
    "RailtownPayload",
    "Breadcrumb",
    "RailtownHandler",
    "RailtownConfig",
    "BreadcrumbManager",
    # Version
    "__version__",
]
