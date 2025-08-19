# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .site_read import SiteRead

__all__ = ["PatientRead"]


class PatientRead(BaseModel):
    id: int

    dob: Optional[date] = None

    email: Optional[str] = None

    family_name: str = FieldInfo(alias="familyName")

    given_name: str = FieldInfo(alias="givenName")

    site_id: int = FieldInfo(alias="siteId")

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")

    cell_phone: Optional[str] = FieldInfo(alias="cellPhone", default=None)

    do_not_call: Optional[bool] = FieldInfo(alias="doNotCall", default=None)

    home_phone: Optional[str] = FieldInfo(alias="homePhone", default=None)

    is_interested_in_research: Optional[bool] = FieldInfo(alias="isInterestedInResearch", default=None)

    last_encounter_date: Optional[date] = FieldInfo(alias="lastEncounterDate", default=None)

    last_patient_activity: Optional[date] = FieldInfo(alias="lastPatientActivity", default=None)

    middle_name: Optional[str] = FieldInfo(alias="middleName", default=None)

    phone: Optional[str] = None

    preferred_language: Optional[Literal["ENGLISH", "SPANISH"]] = FieldInfo(alias="preferredLanguage", default=None)

    primary_provider: Optional[str] = FieldInfo(alias="primaryProvider", default=None)

    provider_first_name: Optional[str] = FieldInfo(alias="providerFirstName", default=None)

    provider_last_name: Optional[str] = FieldInfo(alias="providerLastName", default=None)

    site: Optional[SiteRead] = None

    source: Optional[Literal["EHR", "CSV"]] = None

    zip_code: Optional[str] = FieldInfo(alias="zipCode", default=None)
