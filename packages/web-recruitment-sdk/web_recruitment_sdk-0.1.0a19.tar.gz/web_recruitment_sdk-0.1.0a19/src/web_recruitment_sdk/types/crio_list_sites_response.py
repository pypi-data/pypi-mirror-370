# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["CrioListSitesResponse", "Site", "SiteReferralSource", "SiteStudy"]


class SiteReferralSource(BaseModel):
    id: int

    name: str


class SiteStudy(BaseModel):
    id: str

    name: str

    status: str


class Site(BaseModel):
    id: str

    name: str

    referral_source_category_key: Optional[int] = FieldInfo(alias="referralSourceCategoryKey", default=None)

    referral_sources: List[SiteReferralSource] = FieldInfo(alias="referralSources")

    studies: List[SiteStudy]


class CrioListSitesResponse(BaseModel):
    sites: List[Site]
