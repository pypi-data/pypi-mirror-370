# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SystemSearchEntitiesParams"]


class SystemSearchEntitiesParams(TypedDict, total=False):
    search_text: Required[Annotated[str, PropertyInfo(alias="searchText")]]
    """Text to search for similar entities"""

    limit: int
    """Maximum number of results to return"""

    similarity_threshold: Annotated[Optional[float], PropertyInfo(alias="similarityThreshold")]
    """Minimum similarity score for returned entities"""
