# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CrioListSitesParams"]


class CrioListSitesParams(TypedDict, total=False):
    client_id: Required[str]

    tenant_id: Required[str]
