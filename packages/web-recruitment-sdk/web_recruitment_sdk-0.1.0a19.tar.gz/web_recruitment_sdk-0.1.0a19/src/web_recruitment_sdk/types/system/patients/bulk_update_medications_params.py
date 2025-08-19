# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateMedicationsParams", "Body"]


class BulkUpdateMedicationsParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    cui: Required[str]

    name: Required[str]

    trially_medication_id: Required[Annotated[str, PropertyInfo(alias="triallyMedicationId")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    date_started: Annotated[Union[str, datetime, None], PropertyInfo(alias="dateStarted", format="iso8601")]

    date_stopped: Annotated[Union[str, datetime, None], PropertyInfo(alias="dateStopped", format="iso8601")]

    dosage: Optional[str]

    form: Optional[str]
