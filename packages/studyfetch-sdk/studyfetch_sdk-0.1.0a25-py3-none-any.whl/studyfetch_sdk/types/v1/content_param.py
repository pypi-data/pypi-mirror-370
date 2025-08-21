# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ContentParam"]


class ContentParam(TypedDict, total=False):
    type: Required[Literal["text", "pdf", "video", "audio", "url"]]
    """Type of content"""

    source_url: Annotated[str, PropertyInfo(alias="sourceUrl")]
    """URL to fetch content from"""

    text: str
    """Text content (for text type)"""

    url: str
    """URL to the content (for url type)"""
