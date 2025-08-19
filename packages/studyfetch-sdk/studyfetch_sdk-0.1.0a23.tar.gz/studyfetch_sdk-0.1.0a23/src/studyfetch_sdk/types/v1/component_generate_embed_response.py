# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ComponentGenerateEmbedResponse", "Options"]


class Options(BaseModel):
    height: Optional[str] = None
    """Embed height"""

    width: Optional[str] = None
    """Embed width"""


class ComponentGenerateEmbedResponse(BaseModel):
    token: str
    """JWT token for authentication"""

    component_id: str = FieldInfo(alias="componentId")
    """Component ID"""

    component_type: str = FieldInfo(alias="componentType")
    """Component type"""

    embed_url: str = FieldInfo(alias="embedUrl")
    """The embed URL for iframe integration"""

    expires_at: datetime = FieldInfo(alias="expiresAt")
    """Token expiration timestamp"""

    options: Options
    """Embed options"""
