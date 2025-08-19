# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ProtocolParsingSetErrorParams"]


class ProtocolParsingSetErrorParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    status_message: Optional[str]
