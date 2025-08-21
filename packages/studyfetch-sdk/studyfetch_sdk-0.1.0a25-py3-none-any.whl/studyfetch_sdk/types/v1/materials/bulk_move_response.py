# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["BulkMoveResponse"]


class BulkMoveResponse(BaseModel):
    moved_count: float = FieldInfo(alias="movedCount")
    """Number of materials moved"""

    success: bool
    """Operation success status"""
