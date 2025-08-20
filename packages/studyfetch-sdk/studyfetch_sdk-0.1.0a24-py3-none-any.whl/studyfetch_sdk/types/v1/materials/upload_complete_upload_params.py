# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["UploadCompleteUploadParams"]


class UploadCompleteUploadParams(TypedDict, total=False):
    material_id: Required[Annotated[str, PropertyInfo(alias="materialId")]]
    """Material ID from presigned URL response"""

    s3_key: Required[Annotated[str, PropertyInfo(alias="s3Key")]]
    """S3 key from presigned URL response"""
