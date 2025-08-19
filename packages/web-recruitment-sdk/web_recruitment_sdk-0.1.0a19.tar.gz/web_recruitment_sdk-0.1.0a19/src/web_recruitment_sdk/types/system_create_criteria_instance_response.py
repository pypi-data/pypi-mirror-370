# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .criteria_instance_answer import CriteriaInstanceAnswer

__all__ = ["SystemCreateCriteriaInstanceResponse", "SystemCreateCriteriaInstanceResponseItem"]


class SystemCreateCriteriaInstanceResponseItem(BaseModel):
    id: int

    answer: CriteriaInstanceAnswer

    criteria_id: int = FieldInfo(alias="criteriaId")

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")

    explanation: Optional[str] = None

    match: Optional[bool] = None


SystemCreateCriteriaInstanceResponse: TypeAlias = List[SystemCreateCriteriaInstanceResponseItem]
