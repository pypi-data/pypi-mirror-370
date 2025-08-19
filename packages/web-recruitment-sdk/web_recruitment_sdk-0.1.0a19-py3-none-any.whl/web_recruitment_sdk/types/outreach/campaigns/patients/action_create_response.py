# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ....._utils import PropertyInfo
from ....._models import BaseModel

__all__ = ["ActionCreateResponse", "PhoneCallActionRead", "SMSActionRead"]


class PhoneCallActionRead(BaseModel):
    id: int

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    type: Literal["PHONE_CALL"]

    caller_phone_number: Optional[str] = FieldInfo(alias="callerPhoneNumber", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    duration_seconds: Optional[int] = FieldInfo(alias="durationSeconds", default=None)

    previous_action_id: Optional[int] = FieldInfo(alias="previousActionId", default=None)

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    status: Optional[
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
    ] = None
    """Status values specific to phone call actions"""

    transcript_url: Optional[str] = FieldInfo(alias="transcriptUrl", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class SMSActionRead(BaseModel):
    id: int

    patient_campaign_id: int = FieldInfo(alias="patientCampaignId")

    task_id: int = FieldInfo(alias="taskId")

    type: Literal["SMS"]

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    message: Optional[str] = None

    previous_action_id: Optional[int] = FieldInfo(alias="previousActionId", default=None)

    recipient_phone_number: Optional[str] = FieldInfo(alias="recipientPhoneNumber", default=None)

    sender_phone_number: Optional[str] = FieldInfo(alias="senderPhoneNumber", default=None)

    status: Optional[
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
    ] = None
    """Status values specific to SMS actions"""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


ActionCreateResponse: TypeAlias = Annotated[
    Union[PhoneCallActionRead, SMSActionRead], PropertyInfo(discriminator="type")
]
