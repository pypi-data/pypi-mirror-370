# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["SystemCreateEntitySearchIndexParams"]


class SystemCreateEntitySearchIndexParams(TypedDict, total=False):
    override_num_leaves: Optional[int]
    """Override computed num_leaves"""

    recreate: bool
    """Drop and recreate the index"""
