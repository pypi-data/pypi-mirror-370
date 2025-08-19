# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PatientUpdateParams"]


class PatientUpdateParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    do_not_call: Required[Annotated[bool, PropertyInfo(alias="doNotCall")]]
