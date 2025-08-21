# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["CrawlCreateGraphResponse"]


class CrawlCreateGraphResponse(BaseModel):
    absolute_only: bool

    batch_size: int

    crawl_id: str

    depth_reached: int

    keep_external: bool

    max_depth: int

    max_urls: int

    max_workers: int

    root_url: str

    timestamp: str

    total_pages_visited: int

    visit_external: bool

    visited_urls: List[str]

    debug_frame: Optional[List[Dict[str, object]]] = None
