# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .folder_metadata import FolderMetadata

__all__ = ["FolderGetTreeResponse", "FolderGetTreeResponseItem"]


class FolderGetTreeResponseItem(BaseModel):
    api_id: object = FieldInfo(alias="_id")
    """Folder ID"""

    name: str
    """Folder name"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    status: Literal["active", "deleted"]
    """Folder status"""

    subfolders: List[object]
    """Nested subfolders"""

    created_at: Optional[object] = FieldInfo(alias="createdAt", default=None)
    """Creation date"""

    description: Optional[str] = None
    """Folder description"""

    metadata: Optional[FolderMetadata] = None
    """Folder metadata"""

    parent_folder_id: Optional[str] = FieldInfo(alias="parentFolderId", default=None)
    """Parent folder ID"""

    updated_at: Optional[object] = FieldInfo(alias="updatedAt", default=None)
    """Last update date"""


FolderGetTreeResponse: TypeAlias = List[FolderGetTreeResponseItem]
