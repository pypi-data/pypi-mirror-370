# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["MatchingJobCreateParams"]


class MatchingJobCreateParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    site_ids: Optional[Iterable[int]]
    """List of site IDs to create matching jobs for.

    If not provided, jobs will be created for all sites.
    """
