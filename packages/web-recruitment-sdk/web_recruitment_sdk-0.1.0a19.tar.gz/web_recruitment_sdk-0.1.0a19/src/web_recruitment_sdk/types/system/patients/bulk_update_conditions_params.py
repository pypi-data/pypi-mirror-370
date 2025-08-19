# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateConditionsParams", "Body"]


class BulkUpdateConditionsParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    cui: Required[str]

    name: Required[str]

    trially_condition_id: Required[Annotated[str, PropertyInfo(alias="triallyConditionId")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    category: Optional[str]

    date_started: Annotated[Union[str, datetime, None], PropertyInfo(alias="dateStarted", format="iso8601")]

    date_stopped: Annotated[Union[str, datetime, None], PropertyInfo(alias="dateStopped", format="iso8601")]
