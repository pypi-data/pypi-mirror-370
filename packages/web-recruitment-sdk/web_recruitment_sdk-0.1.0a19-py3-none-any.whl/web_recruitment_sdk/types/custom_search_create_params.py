# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["CustomSearchCreateParams"]


class CustomSearchCreateParams(TypedDict, total=False):
    title: Required[str]

    site_ids: Annotated[Iterable[int], PropertyInfo(alias="siteIds")]
    """The site IDs to associate with the custom search"""
