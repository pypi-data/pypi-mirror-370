# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkMoveParams"]


class BulkMoveParams(TypedDict, total=False):
    folder_id: Required[Annotated[Optional[str], PropertyInfo(alias="folderId")]]
    """Target folder ID (null for root)"""

    material_ids: Required[Annotated[List[str], PropertyInfo(alias="materialIds")]]
    """Array of material IDs to move"""
