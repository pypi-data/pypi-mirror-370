# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateDemographicsParams", "Body"]


class BulkUpdateDemographicsParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    ethnicity: Optional[str]

    gender: Optional[str]

    race: Optional[str]
