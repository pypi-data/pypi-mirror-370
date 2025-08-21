# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .bulk_download_result import BulkDownloadResult

__all__ = ["DownloadCreateBulkResponse", "Results"]


class Results(BaseModel):
    cached: Optional[List[BulkDownloadResult]] = None

    failed: Optional[List[BulkDownloadResult]] = None

    save_failed: Optional[List[BulkDownloadResult]] = None

    success: Optional[List[BulkDownloadResult]] = None


class DownloadCreateBulkResponse(BaseModel):
    cached_count: int

    crawl_id: str

    failed_count: int

    results: Results
    """Grouped results by status"""

    save_failed_count: int

    success_count: int

    timestamp: str

    total_downloads_attempted: int

    total_urls: int

    debug_frame: Optional[List[Dict[str, object]]] = None
