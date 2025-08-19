# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

__all__ = ["DashboardGetRaceDistributionParams"]


class DashboardGetRaceDistributionParams(TypedDict, total=False):
    custom_search_id: Optional[int]

    limit: int

    matching_criteria_ids: Optional[Iterable[int]]

    protocol_id: Optional[int]
