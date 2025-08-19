# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PatientRetrieveResponse", "Patient", "ScreenedTrial"]


class Patient(BaseModel):
    date_of_birth: str = FieldInfo(alias="dateOfBirth")
    """The date of birth of the patient in YYYY-MM-DD format"""

    first_name: str = FieldInfo(alias="firstName")
    """The first name of the patient"""

    gender: Literal["female", "other", "unknown", "male"]

    last_name: str = FieldInfo(alias="lastName")
    """The last name of the patient"""


class ScreenedTrial(BaseModel):
    score: float
    """The score"""

    trial_name: str = FieldInfo(alias="trialName")
    """The trial name"""


class PatientRetrieveResponse(BaseModel):
    carequality_patient_id: str = FieldInfo(alias="carequalityPatientId")
    """The encrypted CareQuality patient ID (format: encrypted(tenant:patient_id))"""

    patient: Patient
    """The patient"""

    screened_trials: List[ScreenedTrial] = FieldInfo(alias="screenedTrials")
    """The screened trials"""
