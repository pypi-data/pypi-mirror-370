# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UserInviteParams"]


class UserInviteParams(TypedDict, total=False):
    email: Required[str]

    role_ids: Required[
        Annotated[
            List[
                Literal[
                    "trially-system-admin",
                    "trially-tenant-admin",
                    "trially-site-admin",
                    "trially-site-viewer",
                    "trially-identified-data-viewer",
                ]
            ],
            PropertyInfo(alias="roleIds"),
        ]
    ]
    """The list of role names in Authress.

    System admins are not allowed to be added as users.
    """

    site_ids: Annotated[Iterable[int], PropertyInfo(alias="siteIds")]
    """Sites the user will have access to"""
