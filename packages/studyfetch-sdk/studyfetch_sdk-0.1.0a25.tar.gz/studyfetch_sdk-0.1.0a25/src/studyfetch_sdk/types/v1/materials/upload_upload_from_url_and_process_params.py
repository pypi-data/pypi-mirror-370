# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["UploadUploadFromURLAndProcessParams"]


class UploadUploadFromURLAndProcessParams(TypedDict, total=False):
    name: Required[str]
    """Material name"""

    url: Required[str]
    """URL to fetch content from"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID (optional)"""

    poll_interval_ms: Annotated[float, PropertyInfo(alias="pollIntervalMs")]
    """Polling interval in milliseconds (default: 2 seconds)"""

    timeout_ms: Annotated[float, PropertyInfo(alias="timeoutMs")]
    """Maximum time to wait for processing in milliseconds (default: 5 minutes)"""
