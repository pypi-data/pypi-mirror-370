# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .criteria_instance_answer import CriteriaInstanceAnswer

__all__ = ["CriteriaInstanceCreateParam"]


class CriteriaInstanceCreateParam(TypedDict, total=False):
    answer: Required[CriteriaInstanceAnswer]

    criteria_id: Required[Annotated[int, PropertyInfo(alias="criteriaId")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    explanation: Optional[str]

    match: Optional[bool]
