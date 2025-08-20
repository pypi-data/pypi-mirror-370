# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["UploadUploadFromURLParams"]


class UploadUploadFromURLParams(TypedDict, total=False):
    name: Required[str]
    """Material name"""

    url: Required[str]
    """URL to fetch content from"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID (optional)"""
