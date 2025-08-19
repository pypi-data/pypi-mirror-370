# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SystemGetPatientMatchDataParams"]


class SystemGetPatientMatchDataParams(TypedDict, total=False):
    criteria_id: Required[Annotated[int, PropertyInfo(alias="criteriaId")]]

    patient_ids: Required[Annotated[List[str], PropertyInfo(alias="patientIds")]]
