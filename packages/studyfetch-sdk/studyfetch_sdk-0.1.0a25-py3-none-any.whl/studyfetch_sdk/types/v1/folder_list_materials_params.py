# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["FolderListMaterialsParams"]


class FolderListMaterialsParams(TypedDict, total=False):
    limit: str
    """Number of items per page (default: 20, max: 200)"""

    page: str
    """Page number (default: 1)"""

    search: str
    """Search materials by name"""
