# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FolderCreateParams"]


class FolderCreateParams(TypedDict, total=False):
    name: Required[str]
    """Folder name"""

    description: str
    """Folder description"""

    metadata: object
    """Additional metadata"""

    parent_folder_id: Annotated[str, PropertyInfo(alias="parentFolderId")]
    """Parent folder ID"""
