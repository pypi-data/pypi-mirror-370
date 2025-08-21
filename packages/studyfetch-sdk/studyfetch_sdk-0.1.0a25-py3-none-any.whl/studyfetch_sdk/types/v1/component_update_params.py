# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["ComponentUpdateParams"]


class ComponentUpdateParams(TypedDict, total=False):
    status: Literal["draft", "active", "inactive", "processing", "error"]
    """Component status"""
