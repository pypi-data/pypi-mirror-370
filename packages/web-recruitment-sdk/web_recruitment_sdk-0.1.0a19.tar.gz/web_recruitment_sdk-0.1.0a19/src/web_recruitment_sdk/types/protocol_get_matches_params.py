# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

__all__ = ["ProtocolGetMatchesParams"]


class ProtocolGetMatchesParams(TypedDict, total=False):
    matching_criteria_ids: Optional[Iterable[int]]
