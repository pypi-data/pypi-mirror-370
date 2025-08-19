# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..criteria_type import CriteriaType
from .criteria_status import CriteriaStatus

__all__ = ["CriteriaRead"]


class CriteriaRead(BaseModel):
    id: int

    summary: str

    type: CriteriaType

    custom_search_id: Optional[int] = FieldInfo(alias="customSearchId", default=None)

    description: Optional[str] = None

    is_pending_matching: Optional[bool] = FieldInfo(alias="isPendingMatching", default=None)

    protocol_id: Optional[int] = FieldInfo(alias="protocolId", default=None)

    status: Optional[CriteriaStatus] = None

    user_raw_input: Optional[str] = FieldInfo(alias="userRawInput", default=None)
