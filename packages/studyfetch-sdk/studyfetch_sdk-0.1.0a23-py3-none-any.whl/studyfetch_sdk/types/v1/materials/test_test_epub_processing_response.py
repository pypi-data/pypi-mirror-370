# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["TestTestEpubProcessingResponse"]


class TestTestEpubProcessingResponse(BaseModel):
    __test__ = False
    success: bool
    """Test success status"""

    epub_size: Optional[float] = FieldInfo(alias="epubSize", default=None)
    """EPUB file size in bytes"""

    epub_size_mb: Optional[str] = FieldInfo(alias="epubSizeMB", default=None)
    """EPUB file size in MB"""

    error: Optional[str] = None
    """Error message if failed"""

    message: Optional[str] = None
    """Success message"""

    stack: Optional[str] = None
    """Error stack trace"""
