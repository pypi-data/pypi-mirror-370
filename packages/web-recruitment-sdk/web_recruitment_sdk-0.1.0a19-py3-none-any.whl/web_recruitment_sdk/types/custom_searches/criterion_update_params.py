# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..criteria_type import CriteriaType
from .criteria_status import CriteriaStatus

__all__ = ["CriterionUpdateParams"]


class CriterionUpdateParams(TypedDict, total=False):
    path_custom_search_id: Required[Annotated[int, PropertyInfo(alias="custom_search_id")]]

    summary: Required[str]

    type: Required[CriteriaType]

    body_custom_search_id: Annotated[Optional[int], PropertyInfo(alias="customSearchId")]

    description: Optional[str]

    protocol_id: Annotated[Optional[int], PropertyInfo(alias="protocolId")]

    status: CriteriaStatus

    user_raw_input: Annotated[Optional[str], PropertyInfo(alias="userRawInput")]
