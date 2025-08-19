# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["NoteRead"]


class NoteRead(BaseModel):
    id: int

    note: str

    patient_id: int = FieldInfo(alias="patientId")

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user_id: Optional[int] = FieldInfo(alias="userId", default=None)

    username: Optional[str] = None
