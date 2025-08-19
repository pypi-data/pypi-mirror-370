# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .protocol_status import ProtocolStatus

__all__ = ["ProtocolUpdateParams", "Site"]


class ProtocolUpdateParams(TypedDict, total=False):
    external_protocol_id: Annotated[Optional[str], PropertyInfo(alias="externalProtocolId")]

    sites: Optional[Iterable[Site]]

    status: ProtocolStatus

    title: Optional[str]

    version: int


class Site(TypedDict, total=False):
    id: Required[int]

    recruiting: Optional[bool]
    """Field is not necessary.

    Recruiting is assumed to be true if the relationship exists
    """
