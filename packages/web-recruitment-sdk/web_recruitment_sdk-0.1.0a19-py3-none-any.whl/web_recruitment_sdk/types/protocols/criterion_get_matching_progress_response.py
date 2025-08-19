# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = [
    "CriterionGetMatchingProgressResponse",
    "CriterionGetMatchingProgressResponseItem",
    "CriterionGetMatchingProgressResponseItemSiteBreakdown",
]


class CriterionGetMatchingProgressResponseItemSiteBreakdown(BaseModel):
    patients_matched: int = FieldInfo(alias="patientsMatched")

    site_id: int = FieldInfo(alias="siteId")

    site_name: str = FieldInfo(alias="siteName")

    total_patients: int = FieldInfo(alias="totalPatients")


class CriterionGetMatchingProgressResponseItem(BaseModel):
    criterion_id: int = FieldInfo(alias="criterionId")

    patients_matched: int = FieldInfo(alias="patientsMatched")

    total_patients: int = FieldInfo(alias="totalPatients")

    site_breakdown: Optional[List[CriterionGetMatchingProgressResponseItemSiteBreakdown]] = FieldInfo(
        alias="siteBreakdown", default=None
    )


CriterionGetMatchingProgressResponse: TypeAlias = List[CriterionGetMatchingProgressResponseItem]
