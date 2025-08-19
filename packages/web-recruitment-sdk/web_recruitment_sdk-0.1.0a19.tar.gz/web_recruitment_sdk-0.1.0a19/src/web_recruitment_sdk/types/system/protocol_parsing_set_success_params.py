# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from ..custom_searches.criteria_create_param import CriteriaCreateParam

__all__ = ["ProtocolParsingSetSuccessParams"]


class ProtocolParsingSetSuccessParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    criteria_create: Required[Iterable[CriteriaCreateParam]]

    external_protocol_id: Required[str]
