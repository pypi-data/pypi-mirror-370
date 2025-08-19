# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CampaignCreateParams"]


class CampaignCreateParams(TypedDict, total=False):
    action_type: Required[Annotated[Literal["PHONE_CALL", "SMS"], PropertyInfo(alias="actionType")]]
    """Type of outreach action to perform"""

    booking_url: Required[Annotated[str, PropertyInfo(alias="bookingUrl")]]

    end_date: Required[Annotated[Union[str, date], PropertyInfo(alias="endDate", format="iso8601")]]
    """Last day of the campaign (YYYY-MM-DD)"""

    from_phone_number: Required[Annotated[str, PropertyInfo(alias="fromPhoneNumber")]]
    """Phone number to use as the 'from' number for calls"""

    hours_between_attempts: Required[Annotated[int, PropertyInfo(alias="hoursBetweenAttempts")]]
    """Minimum hours between outreach attempts"""

    max_attempts_per_patient: Required[Annotated[int, PropertyInfo(alias="maxAttemptsPerPatient")]]
    """Maximum number of outreach attempts per patient"""

    name: Required[str]

    outreach_hours_end: Required[Annotated[int, PropertyInfo(alias="outreachHoursEnd")]]
    """End hour for outreach in patient's local timezone (0-23)"""

    outreach_hours_start: Required[Annotated[int, PropertyInfo(alias="outreachHoursStart")]]
    """Start hour for outreach in patient's local timezone (0-23)"""

    patient_ids: Required[Annotated[List[str], PropertyInfo(alias="patientIds")]]
    """List of patient IDs to include in campaign"""

    start_date: Required[Annotated[Union[str, date], PropertyInfo(alias="startDate", format="iso8601")]]
    """First day of the campaign (YYYY-MM-DD)"""

    principal_investigator: Annotated[Optional[str], PropertyInfo(alias="principalInvestigator")]
