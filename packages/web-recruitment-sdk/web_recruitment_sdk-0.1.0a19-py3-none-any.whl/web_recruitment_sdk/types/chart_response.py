# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ChartResponse", "Data", "DataBreakdown"]


class DataBreakdown(BaseModel):
    count: int

    label: str

    metadata: Optional[object] = None


class Data(BaseModel):
    breakdown: Optional[List[DataBreakdown]] = None

    label: str

    total: int


class ChartResponse(BaseModel):
    data: List[Data]

    total: int

    metadata: Optional[object] = None
