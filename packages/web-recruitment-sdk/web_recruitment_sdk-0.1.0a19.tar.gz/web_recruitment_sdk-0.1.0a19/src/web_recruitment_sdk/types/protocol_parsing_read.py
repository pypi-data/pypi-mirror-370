# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .protocol_parsing_status import ProtocolParsingStatus

__all__ = ["ProtocolParsingRead"]


class ProtocolParsingRead(BaseModel):
    id: int

    protocol_id: int = FieldInfo(alias="protocolId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    file_url: Optional[str] = FieldInfo(alias="fileUrl", default=None)

    job_id: Optional[str] = FieldInfo(alias="jobId", default=None)

    status: Optional[ProtocolParsingStatus] = None

    status_message: Optional[str] = FieldInfo(alias="statusMessage", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
