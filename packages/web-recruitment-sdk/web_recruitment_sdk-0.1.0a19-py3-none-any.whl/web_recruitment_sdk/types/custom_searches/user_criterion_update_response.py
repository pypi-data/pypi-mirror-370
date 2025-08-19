# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UserCriterionUpdateResponse", "UserCriterionUpdateResponseItem"]


class UserCriterionUpdateResponseItem(BaseModel):
    criteria_id: int = FieldInfo(alias="criteriaId")

    custom_search_id: int = FieldInfo(alias="customSearchId")

    user_id: int = FieldInfo(alias="userId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


UserCriterionUpdateResponse: TypeAlias = List[UserCriterionUpdateResponseItem]
