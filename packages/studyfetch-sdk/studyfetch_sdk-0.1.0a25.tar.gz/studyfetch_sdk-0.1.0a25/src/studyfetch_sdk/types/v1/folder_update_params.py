# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FolderUpdateParams"]


class FolderUpdateParams(TypedDict, total=False):
    description: str
    """New folder description"""

    metadata: object
    """Updated metadata"""

    name: str
    """New folder name"""

    parent_folder_id: Annotated[str, PropertyInfo(alias="parentFolderId")]
    """New parent folder ID"""
