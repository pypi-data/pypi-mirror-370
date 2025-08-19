# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["BulkUpdateEntitySearchParams", "Body"]


class BulkUpdateEntitySearchParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    entity: Required[str]

    entity_id: Required[str]

    entity_type: Required[
        Literal["condition", "medication", "allergy", "procedure", "lab_result", "vital_sign", "social_history"]
    ]

    search_text: Required[str]
