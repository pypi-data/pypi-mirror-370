# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["CustomSearchUpdateParams", "Site"]


class CustomSearchUpdateParams(TypedDict, total=False):
    sites: Optional[Iterable[Site]]

    title: Optional[str]


class Site(TypedDict, total=False):
    id: Required[int]
