# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .assignment_grader_response import AssignmentGraderResponse

__all__ = ["AssignmentGraderCreateResponse"]


class AssignmentGraderCreateResponse(BaseModel):
    graded_assignment: Optional[AssignmentGraderResponse] = FieldInfo(alias="gradedAssignment", default=None)

    success: Optional[bool] = None
