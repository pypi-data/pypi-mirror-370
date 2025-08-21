# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .rubric_criterion import RubricCriterion

__all__ = ["RubricTemplateResponse"]


class RubricTemplateResponse(BaseModel):
    api_id: str = FieldInfo(alias="_id")
    """Template ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    created_by: str = FieldInfo(alias="createdBy")
    """Created by user ID"""

    criteria: List[RubricCriterion]
    """Grading criteria"""

    name: str
    """Template name"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Update timestamp"""

    description: Optional[str] = None
    """Template description"""
