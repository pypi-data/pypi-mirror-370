# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["OutreachTriggerCallParams", "CallData", "CallDataSite", "CallDataStudy", "CallDataToPerson"]


class OutreachTriggerCallParams(TypedDict, total=False):
    call_data: Required[CallData]
    """Class to store user data and agents during a call."""

    conversation_flow: Literal["study_qualification", "lead_warmer"]
    """Represents the flow of a conversation."""


class CallDataSite(TypedDict, total=False):
    name: Required[str]

    provider_name: Required[str]


class CallDataStudy(TypedDict, total=False):
    name: Required[str]

    summary: Optional[str]


class CallDataToPerson(TypedDict, total=False):
    first_name: Required[str]

    last_name: Required[str]

    phone_number: Required[str]


class CallData(TypedDict, total=False):
    from_phone_number: Required[str]

    site: Required[CallDataSite]
    """Information about a clinical research site."""

    study: Required[CallDataStudy]
    """Contains information about a clinical study."""

    to_person: Required[CallDataToPerson]
    """Represents a person with contact information and preferences."""

    booking_url: Optional[str]

    patient_campaign_id: Optional[int]

    task_id: Optional[int]
