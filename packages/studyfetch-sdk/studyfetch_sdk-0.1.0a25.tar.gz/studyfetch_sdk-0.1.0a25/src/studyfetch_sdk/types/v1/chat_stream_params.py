# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ChatStreamParams", "Message", "MessageImage"]


class ChatStreamParams(TypedDict, total=False):
    id: str
    """Session ID (AI SDK uses "id")"""

    component_id: Annotated[str, PropertyInfo(alias="componentId")]
    """Component ID"""

    context: object
    """Additional context"""

    group_ids: Annotated[List[str], PropertyInfo(alias="groupIds")]
    """Group IDs for access control"""

    message: Message
    """Single message for custom format - contains text and optional images"""

    messages: List[str]
    """Messages array for AI SDK format - list of conversation messages with roles"""

    session_id: Annotated[str, PropertyInfo(alias="sessionId")]
    """Session ID"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID"""

    x_component_id: Annotated[str, PropertyInfo(alias="x-component-id")]


class MessageImage(TypedDict, total=False):
    base64: str
    """Base64 encoded image data"""

    caption: str
    """Caption for the image"""

    mime_type: Annotated[str, PropertyInfo(alias="mimeType")]
    """MIME type of the image"""

    url: str
    """URL of the image"""


class Message(TypedDict, total=False):
    images: Iterable[MessageImage]
    """Images attached to the message"""

    text: str
    """Text content of the message"""
