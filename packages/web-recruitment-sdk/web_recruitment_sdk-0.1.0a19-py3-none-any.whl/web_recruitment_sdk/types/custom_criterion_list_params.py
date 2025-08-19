# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .criteria_type import CriteriaType

__all__ = ["CustomCriterionListParams"]


class CustomCriterionListParams(TypedDict, total=False):
    criterion_type: Required[CriteriaType]

    free_text: Required[str]
