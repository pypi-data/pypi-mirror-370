# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MaterialSearchResponse", "Result", "ResultMaterial", "Scope"]


class ResultMaterial(BaseModel):
    id: Optional[str] = None

    content_type: Optional[str] = FieldInfo(alias="contentType", default=None)

    name: Optional[str] = None


class Result(BaseModel):
    chunk_index: float = FieldInfo(alias="chunkIndex")
    """Chunk index within the material"""

    material: Optional[ResultMaterial] = None
    """Material information"""

    score: float
    """Relevance score (0-1)"""

    text: str
    """Matched text chunk"""


class Scope(BaseModel):
    folder_ids: Optional[List[str]] = FieldInfo(alias="folderIds", default=None)

    material_ids: Optional[List[str]] = FieldInfo(alias="materialIds", default=None)


class MaterialSearchResponse(BaseModel):
    filtered: bool
    """Whether results were filtered by scope"""

    query: str
    """Original search query"""

    results: List[Result]
    """Search results"""

    scope: Scope
    """Search scope"""

    total_results: float = FieldInfo(alias="totalResults")
    """Total number of results"""
