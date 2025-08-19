# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .protocol_status import ProtocolStatus
from .protocol_parsing_status import ProtocolParsingStatus

__all__ = ["ProtocolRead", "ProtocolParsing", "Site"]


class ProtocolParsing(BaseModel):
    id: int

    file_url: Optional[str] = FieldInfo(alias="fileUrl", default=None)

    job_id: Optional[str] = FieldInfo(alias="jobId", default=None)

    status: Optional[ProtocolParsingStatus] = None

    status_message: Optional[str] = FieldInfo(alias="statusMessage", default=None)


class Site(BaseModel):
    id: int

    name: str

    is_on_carequality: Optional[bool] = FieldInfo(alias="isOnCarequality", default=None)

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    recruiting: Optional[bool] = None
    """Field is not necessary.

    Recruiting is assumed to be true if the relationship exists
    """

    trially_site_id: Optional[str] = FieldInfo(alias="triallySiteId", default=None)

    zip_code: Optional[str] = FieldInfo(alias="zipCode", default=None)


class ProtocolRead(BaseModel):
    id: int

    created_at: datetime = FieldInfo(alias="createdAt")

    external_protocol_id: Optional[str] = FieldInfo(alias="externalProtocolId", default=None)

    protocol_parsing: Optional[ProtocolParsing] = FieldInfo(alias="protocolParsing", default=None)

    title: str

    sites: Optional[List[Site]] = None

    status: Optional[ProtocolStatus] = None

    version: Optional[int] = None
