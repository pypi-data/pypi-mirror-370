# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = ["CriterionGetPatientsToMatchResponse", "CriterionGetPatientsToMatchResponseItem"]


class CriterionGetPatientsToMatchResponseItem(BaseModel):
    trially_patient_id: str

    updated_at: datetime


CriterionGetPatientsToMatchResponse: TypeAlias = List[CriterionGetPatientsToMatchResponseItem]
