# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["UploadGetPresignedURLParams"]


class UploadGetPresignedURLParams(TypedDict, total=False):
    content_type: Required[Annotated[str, PropertyInfo(alias="contentType")]]
    """MIME type of the file"""

    filename: Required[str]
    """Filename to upload"""

    name: Required[str]
    """Display name for the material"""

    extract_images: Annotated[bool, PropertyInfo(alias="extractImages")]
    """Whether to extract images from files"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID to place the material in"""
