# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RubricCriterionParam"]


class RubricCriterionParam(TypedDict, total=False):
    points_possible: Required[Annotated[float, PropertyInfo(alias="pointsPossible")]]
    """Points possible for this criterion"""

    title: Required[str]
    """Title of the criterion"""

    description: str
    """Description of the criterion"""
