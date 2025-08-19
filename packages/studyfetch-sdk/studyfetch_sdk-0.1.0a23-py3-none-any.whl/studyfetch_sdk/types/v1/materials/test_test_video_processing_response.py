# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["TestTestVideoProcessingResponse"]


class TestTestVideoProcessingResponse(BaseModel):
    __test__ = False
    success: bool
    """Test success status"""

    error: Optional[str] = None
    """Error message if failed"""

    message: Optional[str] = None
    """Success message"""

    stack: Optional[str] = None
    """Error stack trace"""

    tests: Optional[object] = None
    """Test results"""
