# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MaterialRenameParams"]


class MaterialRenameParams(TypedDict, total=False):
    name: Required[str]
    """New name for the material"""
