# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .material_response import MaterialResponse

__all__ = ["MaterialListResponse"]


class MaterialListResponse(BaseModel):
    materials: Optional[List[MaterialResponse]] = None

    page: Optional[float] = None

    total_count: Optional[float] = FieldInfo(alias="totalCount", default=None)

    total_pages: Optional[float] = FieldInfo(alias="totalPages", default=None)
