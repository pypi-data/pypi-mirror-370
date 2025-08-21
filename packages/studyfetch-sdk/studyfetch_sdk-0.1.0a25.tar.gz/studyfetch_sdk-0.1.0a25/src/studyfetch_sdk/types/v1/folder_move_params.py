# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FolderMoveParams"]


class FolderMoveParams(TypedDict, total=False):
    parent_folder_id: Required[Annotated[Optional[str], PropertyInfo(alias="parentFolderId")]]
    """New parent folder ID or null for root level"""
