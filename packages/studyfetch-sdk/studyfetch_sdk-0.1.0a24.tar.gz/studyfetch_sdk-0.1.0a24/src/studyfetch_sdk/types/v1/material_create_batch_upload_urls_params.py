# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MaterialCreateBatchUploadURLsParams", "Material"]


class MaterialCreateBatchUploadURLsParams(TypedDict, total=False):
    materials: Required[Iterable[Material]]
    """Array of materials to create"""


class Material(TypedDict, total=False):
    content_type: Required[Annotated[str, PropertyInfo(alias="contentType")]]
    """MIME type"""

    filename: Required[str]
    """Filename"""

    name: Required[str]
    """Material name"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID"""
