# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MatchingTaskRead"]


class MatchingTaskRead(BaseModel):
    id: int

    batch_number: int = FieldInfo(alias="batchNumber")

    batch_size: int = FieldInfo(alias="batchSize")

    job_id: int = FieldInfo(alias="jobId")

    task_name: str = FieldInfo(alias="taskName")

    cancelled_at: Optional[datetime] = FieldInfo(alias="cancelledAt", default=None)

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    error_reason: Optional[str] = FieldInfo(alias="errorReason", default=None)

    status: Optional[Literal["PENDING", "IN_PROGRESS", "SUCCESS", "ERROR", "CANCELLED"]] = None
    """Enum for the status of an external task."""

    storage_url: Optional[str] = FieldInfo(alias="storageUrl", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
