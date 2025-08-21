# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .scrape_engine_param import ScrapeEngineParam

__all__ = ["ScrapeScrapeSingleParams"]


class ScrapeScrapeSingleParams(TypedDict, total=False):
    engines: Required[Iterable[ScrapeEngineParam]]
    """List of engines to use"""

    url: Required[str]
