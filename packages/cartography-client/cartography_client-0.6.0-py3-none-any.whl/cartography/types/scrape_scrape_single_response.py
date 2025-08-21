# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ScrapeScrapeSingleResponse"]


class ScrapeScrapeSingleResponse(BaseModel):
    composite_hash: Optional[str] = None

    content: Optional[str] = None

    content_hash: Optional[str] = None

    status_code: Optional[int] = None

    url: str

    url_hash: Optional[str] = None

    error: Optional[str] = None
