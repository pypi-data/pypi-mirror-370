# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .bulk_scrape_result import BulkScrapeResult

__all__ = ["ScrapeScrapeBulkResponse", "Results"]


class Results(BaseModel):
    cached: Optional[List[BulkScrapeResult]] = None

    failed: Optional[List[BulkScrapeResult]] = None

    save_failed: Optional[List[BulkScrapeResult]] = None

    success: Optional[List[BulkScrapeResult]] = None


class ScrapeScrapeBulkResponse(BaseModel):
    cached_count: int

    crawl_id: str

    failed_count: int

    results: Results
    """Grouped results by status"""

    save_failed_count: int

    success_count: int

    timestamp: str

    total_pages_visited: int

    total_urls: int

    debug_frame: Optional[List[Dict[str, object]]] = None
