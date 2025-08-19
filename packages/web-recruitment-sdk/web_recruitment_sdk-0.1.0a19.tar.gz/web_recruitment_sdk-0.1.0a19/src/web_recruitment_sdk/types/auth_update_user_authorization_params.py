# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AuthUpdateUserAuthorizationParams"]


class AuthUpdateUserAuthorizationParams(TypedDict, total=False):
    role_ids: Annotated[Optional[List[str]], PropertyInfo(alias="roleIds")]

    site_ids: Annotated[Optional[Iterable[int]], PropertyInfo(alias="siteIds")]
