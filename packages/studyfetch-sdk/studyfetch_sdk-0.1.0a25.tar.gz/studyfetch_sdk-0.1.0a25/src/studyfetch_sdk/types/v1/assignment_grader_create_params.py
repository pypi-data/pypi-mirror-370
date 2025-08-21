# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .assignment_grader.rubric_criterion_param import RubricCriterionParam

__all__ = ["AssignmentGraderCreateParams", "Rubric"]


class AssignmentGraderCreateParams(TypedDict, total=False):
    title: Required[str]
    """Title of the assignment"""

    assignment_id: Annotated[str, PropertyInfo(alias="assignmentId")]
    """Assignment ID for grouping submissions"""

    material_id: Annotated[str, PropertyInfo(alias="materialId")]
    """Material ID to grade"""

    model: str
    """AI model to use"""

    rubric: Rubric
    """Grading rubric"""

    rubric_template_id: Annotated[str, PropertyInfo(alias="rubricTemplateId")]
    """Rubric template ID to use"""

    student_identifier: Annotated[str, PropertyInfo(alias="studentIdentifier")]
    """Student identifier (email or ID)"""

    text_to_grade: Annotated[str, PropertyInfo(alias="textToGrade")]
    """Text content to grade"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID for tracking"""


class Rubric(TypedDict, total=False):
    criteria: Required[Iterable[RubricCriterionParam]]
    """Grading criteria"""
