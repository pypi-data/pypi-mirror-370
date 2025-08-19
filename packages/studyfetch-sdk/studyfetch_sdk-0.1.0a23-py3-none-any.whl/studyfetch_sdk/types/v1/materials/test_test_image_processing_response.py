# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["TestTestImageProcessingResponse"]


class TestTestImageProcessingResponse(BaseModel):
    __test__ = False
    success: bool
    """Test success status"""

    error: Optional[str] = None
    """Error message if failed"""

    image_info: Optional[object] = FieldInfo(alias="imageInfo", default=None)
    """Image info if no base64 data"""

    message: Optional[str] = None
    """Success message"""

    results: Optional[object] = None
    """Test results"""

    stack: Optional[str] = None
    """Error stack trace"""
