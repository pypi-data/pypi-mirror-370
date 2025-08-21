# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MaterialListParams"]


class MaterialListParams(TypedDict, total=False):
    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Filter by folder ID"""

    limit: str
    """Number of items per page (default: 20, max: 200)"""

    page: str
    """Page number (default: 1)"""

    search: str
    """Search materials by name"""
