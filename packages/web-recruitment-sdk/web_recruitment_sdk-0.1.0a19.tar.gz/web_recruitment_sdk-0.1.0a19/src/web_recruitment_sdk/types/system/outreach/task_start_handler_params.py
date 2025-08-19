# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["TaskStartHandlerParams"]


class TaskStartHandlerParams(TypedDict, total=False):
    action_type: Required[Annotated[Literal["PHONE_CALL", "SMS"], PropertyInfo(alias="actionType")]]

    booking_url: Required[Annotated[str, PropertyInfo(alias="bookingUrl")]]

    outreach_task_id: Required[Annotated[int, PropertyInfo(alias="outreachTaskId")]]

    patient_campaign_id: Required[Annotated[int, PropertyInfo(alias="patientCampaignId")]]

    scheduled_date: Required[Annotated[Union[str, datetime], PropertyInfo(alias="scheduledDate", format="iso8601")]]
