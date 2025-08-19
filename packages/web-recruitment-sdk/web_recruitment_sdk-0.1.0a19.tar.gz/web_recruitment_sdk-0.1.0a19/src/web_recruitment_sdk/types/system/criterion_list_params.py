# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

__all__ = ["CriterionListParams"]


class CriterionListParams(TypedDict, total=False):
    criteria_ids: Optional[Iterable[int]]
    """List of criteria IDs to match against"""
