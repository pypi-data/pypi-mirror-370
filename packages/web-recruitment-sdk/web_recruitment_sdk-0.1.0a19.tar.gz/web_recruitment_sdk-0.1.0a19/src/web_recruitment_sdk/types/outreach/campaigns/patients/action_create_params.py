# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ....._utils import PropertyInfo

__all__ = ["ActionCreateParams", "PhoneCallActionCreate", "SMSActionCreate"]


class PhoneCallActionCreate(TypedDict, total=False):
    campaign_id: Required[int]

    caller_phone_number: Required[Annotated[str, PropertyInfo(alias="callerPhoneNumber")]]

    duration_seconds: Required[Annotated[int, PropertyInfo(alias="durationSeconds")]]

    recipient_phone_number: Required[Annotated[str, PropertyInfo(alias="recipientPhoneNumber")]]

    status: Required[
        Literal[
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
        ]
    ]
    """Status values specific to phone call actions"""

    task_id: Required[Annotated[int, PropertyInfo(alias="taskId")]]

    type: Required[Literal["PHONE_CALL"]]

    previous_action_id: Annotated[Optional[int], PropertyInfo(alias="previousActionId")]

    transcript_url: Annotated[Optional[str], PropertyInfo(alias="transcriptUrl")]


class SMSActionCreate(TypedDict, total=False):
    campaign_id: Required[int]

    message: Required[str]

    recipient_phone_number: Required[Annotated[str, PropertyInfo(alias="recipientPhoneNumber")]]

    sender_phone_number: Required[Annotated[str, PropertyInfo(alias="senderPhoneNumber")]]

    status: Required[
        Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ]
    ]
    """Status values specific to SMS actions"""

    task_id: Required[Annotated[int, PropertyInfo(alias="taskId")]]

    type: Required[Literal["SMS"]]

    previous_action_id: Annotated[Optional[int], PropertyInfo(alias="previousActionId")]


ActionCreateParams: TypeAlias = Union[PhoneCallActionCreate, SMSActionCreate]
