# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ExportJobCreateParams", "Patient"]


class ExportJobCreateParams(TypedDict, total=False):
    client_id: Required[Annotated[str, PropertyInfo(alias="clientId")]]

    ctms: Required[str]

    ctms_site_id: Required[Annotated[str, PropertyInfo(alias="ctmsSiteId")]]

    patients: Required[Iterable[Patient]]

    referral_source_category_key: Required[Annotated[int, PropertyInfo(alias="referralSourceCategoryKey")]]

    referral_source_key: Required[Annotated[int, PropertyInfo(alias="referralSourceKey")]]

    study_id: Required[Annotated[str, PropertyInfo(alias="studyId")]]


class Patient(TypedDict, total=False):
    match_percentage: Required[Annotated[float, PropertyInfo(alias="matchPercentage")]]

    patient_id: Required[Annotated[str, PropertyInfo(alias="patientId")]]
