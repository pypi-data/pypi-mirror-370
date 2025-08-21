# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RubricCriterion"]


class RubricCriterion(BaseModel):
    points_possible: float = FieldInfo(alias="pointsPossible")
    """Points possible for this criterion"""

    title: str
    """Title of the criterion"""

    description: Optional[str] = None
    """Description of the criterion"""
