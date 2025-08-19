# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["SystemGetPatientMatchDataResponse", "SystemGetPatientMatchDataResponseItem"]


class SystemGetPatientMatchDataResponseItem(BaseModel):
    patient_history: List[object]

    trially_patient_id: str

    last_encounter_date: Optional[date] = None

    patient_age: Optional[int] = None

    patient_ethnicity: Optional[str] = None

    patient_gender: Optional[str] = None

    patient_race: Optional[str] = None


SystemGetPatientMatchDataResponse: TypeAlias = List[SystemGetPatientMatchDataResponseItem]
