# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MaterialCreateBatchUploadURLsResponse", "MaterialCreateBatchUploadURLsResponseItem"]


class MaterialCreateBatchUploadURLsResponseItem(BaseModel):
    material_id: str = FieldInfo(alias="materialId")
    """Material ID"""

    name: str
    """Material name"""

    s3_key: str = FieldInfo(alias="s3Key")
    """S3 key"""

    upload_url: str = FieldInfo(alias="uploadUrl")
    """Presigned upload URL"""


MaterialCreateBatchUploadURLsResponse: TypeAlias = List[MaterialCreateBatchUploadURLsResponseItem]
