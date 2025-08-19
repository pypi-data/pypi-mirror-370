# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SystemSearchEntitiesResponse", "Result"]


class Result(BaseModel):
    entity: str

    entity_id: str = FieldInfo(alias="entityId")

    entity_type: Literal[
        "condition", "medication", "allergy", "procedure", "lab_result", "vital_sign", "social_history"
    ] = FieldInfo(alias="entityType")

    similarity_score: float = FieldInfo(alias="similarityScore")
    """Similarity score between 0 and 1"""


class SystemSearchEntitiesResponse(BaseModel):
    result_count: int = FieldInfo(alias="resultCount")

    results: List[Result]

    search_text: str = FieldInfo(alias="searchText")
