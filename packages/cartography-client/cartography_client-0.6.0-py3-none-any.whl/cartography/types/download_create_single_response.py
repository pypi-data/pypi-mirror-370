# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["DownloadCreateSingleResponse"]


class DownloadCreateSingleResponse(BaseModel):
    download_url: str

    s3_bucket: str

    s3_key: str

    success: bool

    error: Optional[str] = None

    job_id: Optional[str] = None
