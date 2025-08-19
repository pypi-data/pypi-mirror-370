# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["PatientSearchParams"]


class PatientSearchParams(TypedDict, total=False):
    date_of_birth: Required[Annotated[str, PropertyInfo(alias="dateOfBirth")]]
    """The date of birth of the patient in YYYY-MM-DD format"""

    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]
    """The first name of the patient"""

    gender: Required[Literal["female", "other", "unknown", "male"]]

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]
    """The last name of the patient"""

    x_api_key: Required[Annotated[str, PropertyInfo(alias="X-API-Key")]]
