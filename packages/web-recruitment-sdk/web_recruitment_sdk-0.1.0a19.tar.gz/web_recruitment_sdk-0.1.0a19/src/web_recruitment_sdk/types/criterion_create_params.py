# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .criteria_type import CriteriaType
from .custom_searches.criteria_status import CriteriaStatus

__all__ = ["CriterionCreateParams"]


class CriterionCreateParams(TypedDict, total=False):
    summary: Required[str]

    type: Required[CriteriaType]

    custom_search_id: Annotated[Optional[int], PropertyInfo(alias="customSearchId")]

    description: Optional[str]

    protocol_id: Annotated[Optional[int], PropertyInfo(alias="protocolId")]

    status: CriteriaStatus

    user_raw_input: Annotated[Optional[str], PropertyInfo(alias="userRawInput")]
