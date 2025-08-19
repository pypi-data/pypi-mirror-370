# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._types import FileTypes
from ...._utils import PropertyInfo

__all__ = ["UploadUploadFileAndProcessParams"]


class UploadUploadFileAndProcessParams(TypedDict, total=False):
    file: Required[FileTypes]

    name: Required[str]
    """Material name"""

    extract_images: Annotated[str, PropertyInfo(alias="extractImages")]
    """Whether to extract images from files (true/false, default: true)"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID (optional)"""

    poll_interval_ms: Annotated[float, PropertyInfo(alias="pollIntervalMs")]
    """Polling interval in milliseconds (default: 2000)"""

    timeout_ms: Annotated[float, PropertyInfo(alias="timeoutMs")]
    """Processing timeout in milliseconds (default: 300000 - 5 minutes)"""
