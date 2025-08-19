# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MaterialGetDownloadURLParams"]


class MaterialGetDownloadURLParams(TypedDict, total=False):
    expires_in: Annotated[float, PropertyInfo(alias="expiresIn")]
    """URL expiration time in seconds (default: 3600)"""
