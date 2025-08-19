# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateHistoryParams", "Body"]


class BulkUpdateHistoryParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    full_medical_history: Required[Annotated[str, PropertyInfo(alias="fullMedicalHistory")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]
