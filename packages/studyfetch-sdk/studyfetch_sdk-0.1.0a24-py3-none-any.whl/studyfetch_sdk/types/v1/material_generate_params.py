# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MaterialGenerateParams"]


class MaterialGenerateParams(TypedDict, total=False):
    name: Required[str]
    """Name for the generated material"""

    topic: Required[str]
    """Topic or context to generate material from"""

    type: Required[Literal["outline", "overview", "notes", "summary"]]
    """Type of material to generate"""

    context: str
    """Additional context or details about the topic"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Target folder ID"""

    length: Literal["short", "medium", "long"]
    """Length of the generated content"""

    level: Literal["high_school", "college", "professional"]
    """Target education level"""
