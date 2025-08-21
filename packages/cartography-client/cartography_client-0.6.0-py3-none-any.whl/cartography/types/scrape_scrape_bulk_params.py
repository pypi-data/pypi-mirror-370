# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, TypedDict

from .scrape_engine_param import ScrapeEngineParam

__all__ = ["ScrapeScrapeBulkParams"]


class ScrapeScrapeBulkParams(TypedDict, total=False):
    crawl_id: Required[str]
    """Unique identifier for this crawl"""

    engines: Required[Iterable[ScrapeEngineParam]]
    """List of engines to use"""

    s3_bucket: Required[str]
    """S3 bucket for checkpointing"""

    urls: Required[List[str]]
    """List of URLs to scrape"""

    batch_size: int
    """URLs per batch"""

    debug: bool
    """Enable debug information"""

    max_workers: int
    """Maximum concurrent workers"""
