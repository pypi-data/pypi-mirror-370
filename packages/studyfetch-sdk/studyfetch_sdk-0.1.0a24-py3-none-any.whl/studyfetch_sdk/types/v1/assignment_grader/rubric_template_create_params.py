# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RubricTemplateCreateParams", "Criterion"]


class RubricTemplateCreateParams(TypedDict, total=False):
    criteria: Required[Iterable[Criterion]]
    """Grading criteria"""

    name: Required[str]
    """Name of the rubric template"""

    description: str
    """Description of the rubric template"""


class Criterion(TypedDict, total=False):
    points_possible: Required[Annotated[float, PropertyInfo(alias="pointsPossible")]]
    """Points possible for this criterion"""

    title: Required[str]
    """Title of the criterion"""

    description: str
    """Description of the criterion"""
