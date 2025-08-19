# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["NoteCreateParams"]


class NoteCreateParams(TypedDict, total=False):
    note: Required[str]

    body_patient_id: Annotated[Optional[int], PropertyInfo(alias="patientId")]

    user_id: Annotated[Optional[int], PropertyInfo(alias="userId")]
