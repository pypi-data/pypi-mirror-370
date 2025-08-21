# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AssignmentGraderResponse"]


class AssignmentGraderResponse(BaseModel):
    api_v: float = FieldInfo(alias="__v")
    """Version key"""

    api_id: str = FieldInfo(alias="_id")
    """Assignment grader ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    grade: float
    """Overall grade percentage"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    rubric: object
    """Grading results"""

    title: str
    """Assignment title"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Update timestamp"""

    assignment_id: Optional[str] = FieldInfo(alias="assignmentId", default=None)
    """Assignment ID for grouping"""

    material_id: Optional[str] = FieldInfo(alias="materialId", default=None)
    """Material ID"""

    rubric_template_id: Optional[str] = FieldInfo(alias="rubricTemplateId", default=None)
    """Rubric template ID"""

    student_identifier: Optional[str] = FieldInfo(alias="studentIdentifier", default=None)
    """Student identifier"""

    text_to_grade: Optional[str] = FieldInfo(alias="textToGrade", default=None)
    """Text that was graded"""

    user_id: Optional[str] = FieldInfo(alias="userId", default=None)
    """User ID"""
