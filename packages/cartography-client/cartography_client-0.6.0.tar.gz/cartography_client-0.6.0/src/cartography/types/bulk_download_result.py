# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["BulkDownloadResult"]


class BulkDownloadResult(BaseModel):
    status: Literal["success", "cached", "failed", "save_failed"]
    """Status of bulk download result"""

    url: str

    error: Optional[str] = None

    job_id: Optional[str] = None

    s3_bucket: Optional[str] = None

    s3_key: Optional[str] = None
