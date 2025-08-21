# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BulkScrapeResult"]


class BulkScrapeResult(BaseModel):
    status: str

    url: str

    composite_hash: Optional[str] = None

    error: Optional[str] = None

    status_code: Optional[int] = None
