# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ScrapeEngineParam"]


class ScrapeEngineParam(TypedDict, total=False):
    engine_type: Required[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]]

    headers: Optional[Dict[str, str]]
    """Custom headers"""

    proxy: Optional[str]
    """Proxy URL"""

    screenshot: Optional[bool]
    """Take screenshot (Playwright only)"""

    timeout: Optional[int]
    """Timeout in milliseconds"""

    wait_for: Optional[str]
    """CSS selector to wait for (Playwright only)"""
