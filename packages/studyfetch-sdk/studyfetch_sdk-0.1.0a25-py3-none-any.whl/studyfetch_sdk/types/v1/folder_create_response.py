# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .folder_metadata import FolderMetadata

__all__ = ["FolderCreateResponse"]


class FolderCreateResponse(BaseModel):
    api_id: str = FieldInfo(alias="_id")
    """Folder ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation date"""

    name: str
    """Folder name"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    status: Literal["active", "deleted"]
    """Folder status"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Last update date"""

    description: Optional[str] = None
    """Folder description"""

    metadata: Optional[FolderMetadata] = None
    """Folder metadata"""

    parent_folder_id: Optional[str] = FieldInfo(alias="parentFolderId", default=None)
    """Parent folder ID"""
