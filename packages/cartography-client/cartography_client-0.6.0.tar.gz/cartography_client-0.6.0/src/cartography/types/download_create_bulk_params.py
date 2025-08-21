# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

from .wait_until import WaitUntil
from .downloader_type import DownloaderType

__all__ = ["DownloadCreateBulkParams"]


class DownloadCreateBulkParams(TypedDict, total=False):
    crawl_id: Required[str]
    """Unique identifier for this crawl"""

    s3_bucket: Required[str]
    """S3 bucket for storage and checkpoints"""

    urls: Required[List[str]]
    """List of URLs to download"""

    batch_size: int
    """URLs per batch"""

    debug: bool
    """Enable debug information"""

    downloader_type: DownloaderType
    """Available downloader types"""

    max_workers: int
    """Maximum concurrent workers"""

    wait_until: WaitUntil
    """When to consider downloads complete"""
