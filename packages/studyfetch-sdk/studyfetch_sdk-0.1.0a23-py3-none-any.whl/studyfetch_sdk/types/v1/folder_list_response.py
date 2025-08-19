# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["FolderListResponse", "FolderListResponseItem", "FolderListResponseItemMetadata"]


class FolderListResponseItemMetadata(BaseModel):
    color: Optional[str] = None
    """Folder color"""

    icon: Optional[str] = None
    """Folder icon"""

    last_activity: Optional[datetime] = FieldInfo(alias="lastActivity", default=None)
    """Last activity date"""

    material_count: Optional[float] = FieldInfo(alias="materialCount", default=None)
    """Number of materials in folder"""

    total_size: Optional[float] = FieldInfo(alias="totalSize", default=None)
    """Total size of materials in folder"""


class FolderListResponseItem(BaseModel):
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

    metadata: Optional[FolderListResponseItemMetadata] = None
    """Folder metadata"""

    parent_folder_id: Optional[str] = FieldInfo(alias="parentFolderId", default=None)
    """Parent folder ID"""


FolderListResponse: TypeAlias = List[FolderListResponseItem]
