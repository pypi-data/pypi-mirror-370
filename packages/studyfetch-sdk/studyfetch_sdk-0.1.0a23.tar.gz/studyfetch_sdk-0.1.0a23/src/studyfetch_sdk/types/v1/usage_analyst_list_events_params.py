# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UsageAnalystListEventsParams"]


class UsageAnalystListEventsParams(TypedDict, total=False):
    end_date: Required[Annotated[str, PropertyInfo(alias="endDate")]]
    """End date for filtering (ISO 8601)"""

    event_type: Required[
        Annotated[
            Literal[
                "material_created",
                "material_uploaded",
                "material_processed",
                "material_deleted",
                "component_created",
                "component_accessed",
                "component_deleted",
                "component_usage",
                "chat_message_sent",
                "chat_session_started",
                "chat_session_ended",
                "chat_feedback",
                "test_created",
                "test_started",
                "test_completed",
                "test_question_answered",
                "test_retaken",
                "audio_recap_create",
                "assignment_grader_create",
                "api_call",
                "cache_hit",
                "sso_login",
                "sso_logout",
                "student_performance",
            ],
            PropertyInfo(alias="eventType"),
        ]
    ]
    """Type of usage event to filter"""

    start_date: Required[Annotated[str, PropertyInfo(alias="startDate")]]
    """Start date for filtering (ISO 8601)"""

    group_ids: Annotated[List[str], PropertyInfo(alias="groupIds")]
    """Array of group IDs to filter"""

    user_ids: Annotated[List[str], PropertyInfo(alias="userIds")]
    """Array of user IDs to filter"""
