# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["SiteCreateResponse"]


class SiteCreateResponse(BaseModel):
    protocol_id: int = FieldInfo(alias="protocolId")

    site_id: int = FieldInfo(alias="siteId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    recruiting: Optional[bool] = None
    """Field is not necessary.

    Recruiting is assumed to be true if the relationship exists
    """

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
