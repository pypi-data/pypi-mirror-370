# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RubricTemplateCreateResponse", "Criterion"]


class Criterion(BaseModel):
    points_possible: float = FieldInfo(alias="pointsPossible")
    """Points possible for this criterion"""

    title: str
    """Title of the criterion"""

    description: Optional[str] = None
    """Description of the criterion"""


class RubricTemplateCreateResponse(BaseModel):
    api_id: str = FieldInfo(alias="_id")
    """Template ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    created_by: str = FieldInfo(alias="createdBy")
    """Created by user ID"""

    criteria: List[Criterion]
    """Grading criteria"""

    name: str
    """Template name"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Update timestamp"""

    description: Optional[str] = None
    """Template description"""
