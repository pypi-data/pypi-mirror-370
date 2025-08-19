# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["FolderRetrieveResponse", "Metadata"]


class Metadata(BaseModel):
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


class FolderRetrieveResponse(BaseModel):
    api_id: object = FieldInfo(alias="_id")
    """Folder ID"""

    material_count: float = FieldInfo(alias="materialCount")
    """Total number of materials"""

    materials: List[object]
    """Materials in this folder"""

    name: str
    """Folder name"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    status: Literal["active", "deleted"]
    """Folder status"""

    subfolders: List[object]
    """Subfolders"""

    total_size: float = FieldInfo(alias="totalSize")
    """Total size of all materials in bytes"""

    created_at: Optional[object] = FieldInfo(alias="createdAt", default=None)
    """Creation date"""

    description: Optional[str] = None
    """Folder description"""

    metadata: Optional[Metadata] = None
    """Folder metadata"""

    parent_folder_id: Optional[str] = FieldInfo(alias="parentFolderId", default=None)
    """Parent folder ID"""

    updated_at: Optional[object] = FieldInfo(alias="updatedAt", default=None)
    """Last update date"""
