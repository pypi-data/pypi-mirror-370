# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CampaignCreateResponse"]


class CampaignCreateResponse(BaseModel):
    id: int

    action_type: Literal["PHONE_CALL", "SMS"] = FieldInfo(alias="actionType")

    booking_url: str = FieldInfo(alias="bookingUrl")

    end_date: date = FieldInfo(alias="endDate")

    from_phone_number: str = FieldInfo(alias="fromPhoneNumber")

    hours_between_attempts: int = FieldInfo(alias="hoursBetweenAttempts")

    max_attempts_per_patient: int = FieldInfo(alias="maxAttemptsPerPatient")

    name: str

    outreach_hours_end: int = FieldInfo(alias="outreachHoursEnd")

    outreach_hours_start: int = FieldInfo(alias="outreachHoursStart")

    start_date: date = FieldInfo(alias="startDate")

    total_candidates: int = FieldInfo(alias="totalCandidates")

    principal_investigator: Optional[str] = FieldInfo(alias="principalInvestigator", default=None)

    status: Optional[Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "PAUSED"]] = None
    """Campaign states"""
