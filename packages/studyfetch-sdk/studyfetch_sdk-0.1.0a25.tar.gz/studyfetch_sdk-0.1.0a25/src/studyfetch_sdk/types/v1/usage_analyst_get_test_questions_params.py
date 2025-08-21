# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UsageAnalystGetTestQuestionsParams"]


class UsageAnalystGetTestQuestionsParams(TypedDict, total=False):
    group_ids: Annotated[List[str], PropertyInfo(alias="groupIds")]
    """Array of group IDs to filter"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID to get test results for"""
