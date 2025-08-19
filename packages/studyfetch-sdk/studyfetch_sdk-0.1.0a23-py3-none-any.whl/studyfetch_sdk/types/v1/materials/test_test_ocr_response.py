# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["TestTestOcrResponse"]


class TestTestOcrResponse(BaseModel):
    __test__ = False
    first_chars: str = FieldInfo(alias="firstChars")
    """First 500 characters of extracted text"""

    success: bool
    """Test success status"""

    text_length: float = FieldInfo(alias="textLength")
    """Length of extracted text"""
