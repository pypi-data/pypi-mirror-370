# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FolderListParams"]


class FolderListParams(TypedDict, total=False):
    parent_id: Annotated[object, PropertyInfo(alias="parentId")]
    """Filter by parent folder"""
