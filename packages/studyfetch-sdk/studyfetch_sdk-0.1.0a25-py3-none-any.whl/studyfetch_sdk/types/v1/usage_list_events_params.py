# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UsageListEventsParams"]


class UsageListEventsParams(TypedDict, total=False):
    end_date: Annotated[str, PropertyInfo(alias="endDate")]
    """End date for filtering (ISO 8601)"""

    event_type: Annotated[
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
    """Filter by event type"""

    group_id: Annotated[str, PropertyInfo(alias="groupId")]
    """Filter by group ID"""

    limit: float
    """Number of results to return"""

    offset: float
    """Offset for pagination"""

    resource_id: Annotated[str, PropertyInfo(alias="resourceId")]
    """Filter by resource ID"""

    start_date: Annotated[str, PropertyInfo(alias="startDate")]
    """Start date for filtering (ISO 8601)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """Filter by user ID"""
