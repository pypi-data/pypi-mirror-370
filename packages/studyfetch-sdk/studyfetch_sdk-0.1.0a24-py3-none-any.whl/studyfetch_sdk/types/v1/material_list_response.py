# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MaterialListResponse"]


class MaterialListResponse(BaseModel):
    data: List[object]
    """Array of materials"""

    limit: float
    """Number of items per page"""

    page: float
    """Current page number"""

    total: float
    """Total number of materials"""

    total_pages: float = FieldInfo(alias="totalPages")
    """Total number of pages"""
