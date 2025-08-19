# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["ProtocolParsingUploadParams"]


class ProtocolParsingUploadParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The protocol file to upload"""

    title: Required[str]
    """The title of the protocol"""

    site_ids: Iterable[int]
    """The site IDs to associate with the protocol"""
