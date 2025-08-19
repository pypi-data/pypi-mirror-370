# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .custom_searches.criteria_status import CriteriaStatus

__all__ = ["CriterionUpdateParams"]


class CriterionUpdateParams(TypedDict, total=False):
    description: Optional[str]

    status: Optional[CriteriaStatus]

    summary: Optional[str]

    user_raw_input: Annotated[Optional[str], PropertyInfo(alias="userRawInput")]
