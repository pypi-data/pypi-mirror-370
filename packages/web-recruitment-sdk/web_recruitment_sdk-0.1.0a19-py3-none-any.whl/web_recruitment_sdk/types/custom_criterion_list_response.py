# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .criteria_type import CriteriaType

__all__ = ["CustomCriterionListResponse"]


class CustomCriterionListResponse(BaseModel):
    description: str

    summary: str

    type: CriteriaType
