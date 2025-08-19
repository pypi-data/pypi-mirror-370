# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["SiteUpdateParams"]


class SiteUpdateParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    is_on_carequality: Annotated[Optional[bool], PropertyInfo(alias="isOnCarequality")]

    name: Optional[str]

    trially_site_id: Annotated[Optional[str], PropertyInfo(alias="triallySiteId")]

    zip_code: Annotated[Optional[str], PropertyInfo(alias="zipCode")]
