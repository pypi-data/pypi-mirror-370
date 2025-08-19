# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateLabResultsParams", "Body"]


class BulkUpdateLabResultsParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    entity_id: Required[Annotated[str, PropertyInfo(alias="entityId")]]

    name: Required[str]

    trially_lab_result_id: Required[Annotated[str, PropertyInfo(alias="triallyLabResultId")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    cui: Optional[str]

    date_started: Annotated[Union[str, datetime, None], PropertyInfo(alias="dateStarted", format="iso8601")]

    unit: Optional[str]

    value: Optional[str]
