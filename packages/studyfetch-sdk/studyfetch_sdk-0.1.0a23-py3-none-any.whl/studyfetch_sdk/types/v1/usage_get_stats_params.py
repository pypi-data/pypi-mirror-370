# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UsageGetStatsParams"]


class UsageGetStatsParams(TypedDict, total=False):
    end_date: Annotated[str, PropertyInfo(alias="endDate")]
    """End date for stats (ISO 8601)"""

    group_id: Annotated[str, PropertyInfo(alias="groupId")]
    """Filter by group ID"""

    start_date: Annotated[str, PropertyInfo(alias="startDate")]
    """Start date for stats (ISO 8601)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """Filter by user ID"""
