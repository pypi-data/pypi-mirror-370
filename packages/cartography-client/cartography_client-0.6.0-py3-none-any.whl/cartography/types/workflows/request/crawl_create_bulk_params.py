# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .crawl_request_param import CrawlRequestParam

__all__ = ["CrawlCreateBulkParams"]


class CrawlCreateBulkParams(TypedDict, total=False):
    jobs: Required[Iterable[CrawlRequestParam]]
