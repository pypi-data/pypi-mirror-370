# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["FolderMetadata"]


class FolderMetadata(BaseModel):
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
