# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .wait_until import WaitUntil
from .downloader_type import DownloaderType

__all__ = ["DownloadCreateSingleParams"]


class DownloadCreateSingleParams(TypedDict, total=False):
    s3_bucket: Required[str]
    """S3 bucket for storage"""

    url: Required[str]
    """URL to download"""

    downloader_type: DownloaderType
    """Available downloader types"""

    s3_key: Optional[str]
    """S3 key for the file"""

    api_timeout: Annotated[int, PropertyInfo(alias="timeout")]
    """Timeout in milliseconds"""

    wait_until: WaitUntil
    """When to consider download complete"""
