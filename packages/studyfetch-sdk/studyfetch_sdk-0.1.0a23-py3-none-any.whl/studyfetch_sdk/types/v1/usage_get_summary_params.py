# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UsageGetSummaryParams"]


class UsageGetSummaryParams(TypedDict, total=False):
    end_date: Required[Annotated[str, PropertyInfo(alias="endDate")]]
    """End date for summary (ISO 8601)"""

    period: Required[Literal["hourly", "daily", "monthly"]]
    """Summary period"""

    start_date: Required[Annotated[str, PropertyInfo(alias="startDate")]]
    """Start date for summary (ISO 8601)"""

    group_by: Annotated[Literal["user", "group", "model", "endpoint"], PropertyInfo(alias="groupBy")]
    """Group results by"""
