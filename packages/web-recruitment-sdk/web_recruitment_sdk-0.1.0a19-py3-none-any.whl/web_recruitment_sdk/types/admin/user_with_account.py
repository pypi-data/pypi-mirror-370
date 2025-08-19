# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..authorization import Authorization

__all__ = ["UserWithAccount", "Account"]


class Account(BaseModel):
    id: int

    name: str

    tenant: str

    tenant_id: str = FieldInfo(alias="tenantId")
    """An external identifier for the tenant, e.g. the Authress tenant ID"""

    has_carequality_sites: Optional[bool] = FieldInfo(alias="hasCarequalitySites", default=None)


class UserWithAccount(BaseModel):
    id: int

    email: str

    invite_status: Literal["sent", "accepted"] = FieldInfo(alias="inviteStatus")

    account: Optional[Account] = None

    authorization: Optional[Authorization] = None

    auth_user_id: Optional[str] = FieldInfo(alias="authUserId", default=None)

    invite_accepted_at: Optional[datetime] = FieldInfo(alias="inviteAcceptedAt", default=None)

    invite_id: Optional[str] = FieldInfo(alias="inviteId", default=None)

    name: Optional[str] = None

    profile_picture: Optional[str] = FieldInfo(alias="profilePicture", default=None)
