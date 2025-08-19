# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ...._utils import PropertyInfo
from ...._models import BaseModel
from ...patient_read import PatientRead

__all__ = [
    "PatientListResponse",
    "PatientListResponseItem",
    "PatientListResponseItemOutreachAction",
    "PatientListResponseItemOutreachActionPhoneCallActionRead",
    "PatientListResponseItemOutreachActionSMSActionRead",
]


class PatientListResponseItemOutreachActionPhoneCallActionRead(BaseModel):
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


class PatientListResponseItemOutreachActionSMSActionRead(BaseModel):
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


PatientListResponseItemOutreachAction: TypeAlias = Annotated[
    Union[PatientListResponseItemOutreachActionPhoneCallActionRead, PatientListResponseItemOutreachActionSMSActionRead],
    PropertyInfo(discriminator="type"),
]


class PatientListResponseItem(BaseModel):
    id: int

    campaign_id: int = FieldInfo(alias="campaignId")

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")

    outreach_actions: Optional[List[PatientListResponseItemOutreachAction]] = FieldInfo(
        alias="outreachActions", default=None
    )

    patient: Optional[PatientRead] = None

    status: Optional[Literal["NOT_STARTED", "IN_PROGRESS", "SUCCESSFUL", "UNSUCCESSFUL"]] = None
    """Patient's journey state within a campaign"""


PatientListResponse: TypeAlias = List[PatientListResponseItem]
