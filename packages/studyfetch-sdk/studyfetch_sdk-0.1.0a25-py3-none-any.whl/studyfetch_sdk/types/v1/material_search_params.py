# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MaterialSearchParams"]


class MaterialSearchParams(TypedDict, total=False):
    query: Required[str]
    """Search query"""

    folder_ids: Annotated[List[str], PropertyInfo(alias="folderIds")]
    """Limit search to materials within specific folders (includes subfolders)"""

    material_ids: Annotated[List[str], PropertyInfo(alias="materialIds")]
    """Limit search to specific material IDs"""

    top_k: Annotated[float, PropertyInfo(alias="topK")]
    """Number of results to return"""
