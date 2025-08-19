# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BulkUpdateEntityParams", "Body"]


class BulkUpdateEntityParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    entity_id: Required[str]

    trially_patient_id: Required[str]

    date_started: Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]

    date_stopped: Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]
