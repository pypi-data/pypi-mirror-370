# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from ..patient_create_param import PatientCreateParam

__all__ = ["BulkUpsertParams"]


class BulkUpsertParams(TypedDict, total=False):
    body: Required[Iterable[PatientCreateParam]]
