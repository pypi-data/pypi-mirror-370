# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .rubric_criterion_param import RubricCriterionParam

__all__ = ["RubricTemplateCreateParams"]


class RubricTemplateCreateParams(TypedDict, total=False):
    criteria: Required[Iterable[RubricCriterionParam]]
    """Grading criteria"""

    name: Required[str]
    """Name of the rubric template"""

    description: str
    """Description of the rubric template"""
