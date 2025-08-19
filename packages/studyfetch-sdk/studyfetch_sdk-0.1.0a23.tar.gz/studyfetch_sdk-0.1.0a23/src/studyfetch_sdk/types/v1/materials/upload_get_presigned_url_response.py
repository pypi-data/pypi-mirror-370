# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["UploadGetPresignedURLResponse"]


class UploadGetPresignedURLResponse(BaseModel):
    material_id: str = FieldInfo(alias="materialId")
    """Material ID to use for completion"""

    s3_key: str = FieldInfo(alias="s3Key")
    """S3 key for the file"""

    upload_url: str = FieldInfo(alias="uploadUrl")
    """Presigned URL for direct S3 upload"""
