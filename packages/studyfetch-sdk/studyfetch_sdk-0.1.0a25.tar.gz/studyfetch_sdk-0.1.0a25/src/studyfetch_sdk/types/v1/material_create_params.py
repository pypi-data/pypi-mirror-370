# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .content_param import ContentParam

__all__ = ["MaterialCreateParams"]


class MaterialCreateParams(TypedDict, total=False):
    content: Required[ContentParam]
    """Content details"""

    name: Required[str]
    """Name of the material"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID to place the material in"""
