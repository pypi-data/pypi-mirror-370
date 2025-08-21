# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .workflow_result import WorkflowResult

__all__ = ["CrawlCreateBulkResponse", "Error"]


class Error(BaseModel):
    error: str

    url: Optional[str] = None

    workflow_id: Optional[str] = None


class CrawlCreateBulkResponse(BaseModel):
    results: List[WorkflowResult]

    errors: Optional[List[Error]] = None
