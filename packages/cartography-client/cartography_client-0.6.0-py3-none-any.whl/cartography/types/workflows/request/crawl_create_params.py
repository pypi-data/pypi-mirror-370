# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CrawlCreateParams"]


class CrawlCreateParams(TypedDict, total=False):
    bucket_name: Required[str]

    crawl_id: Required[str]

    engines: Required[List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]]]

    url: Required[str]

    absolute_only: bool

    batch_size: int

    depth: int

    keep_external: bool

    max_urls: int

    max_workers: int

    stealth: bool

    visit_external: bool
