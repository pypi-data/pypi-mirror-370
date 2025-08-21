# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MaterialGetDebugInfoResponse", "Image"]


class Image(BaseModel):
    id: Optional[str] = None

    description: Optional[str] = None

    page_index: Optional[float] = FieldInfo(alias="pageIndex", default=None)

    s3_key: Optional[str] = FieldInfo(alias="s3Key", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3Url", default=None)


class MaterialGetDebugInfoResponse(BaseModel):
    content: object
    """Content details"""

    content_type: str = FieldInfo(alias="contentType")
    """Content type"""

    images: List[Image]
    """Processed images"""

    material_id: str = FieldInfo(alias="materialId")
    """Material ID"""

    metadata: object
    """Material metadata"""

    name: str
    """Material name"""

    status: str
    """Processing status"""

    transcript_structure: Optional[object] = FieldInfo(alias="transcriptStructure", default=None)
    """Transcript structure for videos"""
