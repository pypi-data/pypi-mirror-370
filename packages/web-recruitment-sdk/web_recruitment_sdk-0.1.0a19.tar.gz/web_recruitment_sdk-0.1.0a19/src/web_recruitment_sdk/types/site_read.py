# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SiteRead"]


class SiteRead(BaseModel):
    id: int

    name: str

    is_on_carequality: Optional[bool] = FieldInfo(alias="isOnCarequality", default=None)

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    trially_site_id: Optional[str] = FieldInfo(alias="triallySiteId", default=None)

    zip_code: Optional[str] = FieldInfo(alias="zipCode", default=None)
