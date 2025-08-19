# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExportJobRetrievePatientsResponse", "ExportJobRetrievePatientsResponseItem"]


class ExportJobRetrievePatientsResponseItem(BaseModel):
    id: int

    created_at: datetime = FieldInfo(alias="createdAt")

    name: str

    status: str

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


ExportJobRetrievePatientsResponse: TypeAlias = List[ExportJobRetrievePatientsResponseItem]
