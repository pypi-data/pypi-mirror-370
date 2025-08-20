# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UsageAnalystListChatMessagesResponse", "Message"]


class Message(BaseModel):
    component_id: Optional[str] = FieldInfo(alias="componentId", default=None)

    content: Optional[str] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    metadata: Optional[object] = None

    role: Optional[Literal["user", "assistant", "system"]] = None

    session_id: Optional[str] = FieldInfo(alias="sessionId", default=None)

    user_id: Optional[str] = FieldInfo(alias="userId", default=None)


class UsageAnalystListChatMessagesResponse(BaseModel):
    messages: Optional[List[Message]] = None

    session_count: Optional[float] = FieldInfo(alias="sessionCount", default=None)

    total: Optional[float] = None
