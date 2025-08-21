# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MaterialResponse", "Content"]


class Content(BaseModel):
    filename: Optional[str] = None

    file_size: Optional[float] = FieldInfo(alias="fileSize", default=None)

    mime_type: Optional[str] = FieldInfo(alias="mimeType", default=None)

    s3_key: Optional[str] = FieldInfo(alias="s3Key", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3Url", default=None)

    text: Optional[str] = None

    url: Optional[str] = None


class MaterialResponse(BaseModel):
    api_id: str = FieldInfo(alias="_id")
    """Material ID"""

    content: Content
    """Material content"""

    content_type: Literal["text", "pdf", "video", "audio", "image", "epub"] = FieldInfo(alias="contentType")
    """Content type"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    folder_id: Optional[str] = FieldInfo(alias="folderId", default=None)
    """Folder ID"""

    name: str
    """Material name"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    status: Literal["active", "processing", "pending_upload", "error", "deleted"]
    """Material status"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Last update timestamp"""

    metadata: Optional[object] = None
    """Material metadata"""

    usage: Optional[object] = None
    """Usage information"""
