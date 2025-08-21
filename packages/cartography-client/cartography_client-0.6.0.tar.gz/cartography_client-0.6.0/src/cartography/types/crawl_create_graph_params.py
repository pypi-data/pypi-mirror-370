# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CrawlCreateGraphParams"]


class CrawlCreateGraphParams(TypedDict, total=False):
    crawl_id: Required[str]
    """Unique identifier for this crawl"""

    engines: Required[List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]]]
    """List of engines to use"""

    s3_bucket: Required[str]
    """S3 bucket for checkpointing"""

    url: Required[str]
    """Root URL to start crawling from"""

    absolute_only: bool
    """Only extract absolute URLs"""

    batch_size: int
    """URLs per batch"""

    debug: bool
    """Enable debug information"""

    depth: Optional[int]
    """Maximum crawl depth"""

    keep_external: bool
    """Keep external URLs in results"""

    max_urls: int
    """Maximum URLs to crawl"""

    max_workers: int
    """Maximum concurrent workers"""

    visit_external: bool
    """Visit external URLs"""
