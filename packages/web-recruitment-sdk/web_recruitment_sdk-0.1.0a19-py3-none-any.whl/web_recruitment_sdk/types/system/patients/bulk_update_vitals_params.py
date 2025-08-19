# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateVitalsParams", "Body"]


class BulkUpdateVitalsParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    effective_date: Required[Annotated[Union[str, datetime], PropertyInfo(alias="effectiveDate", format="iso8601")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    bmi: Optional[float]

    diastolic_blood_pressure: Annotated[Optional[float], PropertyInfo(alias="diastolicBloodPressure")]

    height_cm: Annotated[Optional[float], PropertyInfo(alias="heightCm")]

    pulse_rate: Annotated[Optional[float], PropertyInfo(alias="pulseRate")]

    respiration_rate: Annotated[Optional[float], PropertyInfo(alias="respirationRate")]

    systolic_blood_pressure: Annotated[Optional[float], PropertyInfo(alias="systolicBloodPressure")]

    weight_kg: Annotated[Optional[float], PropertyInfo(alias="weightKg")]
