# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PatientCreateParams"]


class PatientCreateParams(TypedDict, total=False):
    dob: Required[Annotated[Union[str, date, None], PropertyInfo(format="iso8601")]]

    email: Required[Optional[str]]

    family_name: Required[Annotated[str, PropertyInfo(alias="familyName")]]

    given_name: Required[Annotated[str, PropertyInfo(alias="givenName")]]

    site_id: Required[Annotated[int, PropertyInfo(alias="siteId")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    cell_phone: Annotated[Optional[str], PropertyInfo(alias="cellPhone")]

    do_not_call: Annotated[Optional[bool], PropertyInfo(alias="doNotCall")]

    home_phone: Annotated[Optional[str], PropertyInfo(alias="homePhone")]

    is_interested_in_research: Annotated[Optional[bool], PropertyInfo(alias="isInterestedInResearch")]

    last_encounter_date: Annotated[Union[str, date, None], PropertyInfo(alias="lastEncounterDate", format="iso8601")]

    last_patient_activity: Annotated[
        Union[str, date, None], PropertyInfo(alias="lastPatientActivity", format="iso8601")
    ]

    middle_name: Annotated[Optional[str], PropertyInfo(alias="middleName")]

    phone: Optional[str]

    preferred_language: Annotated[Literal["ENGLISH", "SPANISH"], PropertyInfo(alias="preferredLanguage")]

    primary_provider: Annotated[Optional[str], PropertyInfo(alias="primaryProvider")]

    provider_first_name: Annotated[Optional[str], PropertyInfo(alias="providerFirstName")]

    provider_last_name: Annotated[Optional[str], PropertyInfo(alias="providerLastName")]

    source: Literal["EHR", "CSV"]

    zip_code: Annotated[Optional[str], PropertyInfo(alias="zipCode")]
