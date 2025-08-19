# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UserCriterionUpdateResponse", "UserCriterionUpdateResponseItem"]


class UserCriterionUpdateResponseItem(BaseModel):
    criteria_id: int = FieldInfo(alias="criteriaId")

    protocol_id: int = FieldInfo(alias="protocolId")

    user_id: int = FieldInfo(alias="userId")


UserCriterionUpdateResponse: TypeAlias = List[UserCriterionUpdateResponseItem]
