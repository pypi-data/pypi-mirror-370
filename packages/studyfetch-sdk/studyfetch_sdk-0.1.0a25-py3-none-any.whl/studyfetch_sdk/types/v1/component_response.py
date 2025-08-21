# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ComponentResponse"]


class ComponentResponse(BaseModel):
    api_id: str = FieldInfo(alias="_id")
    """Component ID (MongoDB ObjectId)"""

    component_id: str = FieldInfo(alias="componentId")
    """Unique component identifier"""

    config: object
    """Component configuration"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    name: str
    """Component name"""

    organization: str
    """Organization ID"""

    status: Literal["active", "inactive", "draft"]
    """Component status"""

    type: Literal[
        "chat",
        "data_analyst",
        "flashcards",
        "scenarios",
        "practice_test",
        "audio_recap",
        "tutor_me",
        "explainers",
        "uploads",
        "chat_analytics",
    ]
    """Component type"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Last update timestamp"""

    usage: object
    """Usage statistics"""

    description: Optional[str] = None
    """Component description"""
