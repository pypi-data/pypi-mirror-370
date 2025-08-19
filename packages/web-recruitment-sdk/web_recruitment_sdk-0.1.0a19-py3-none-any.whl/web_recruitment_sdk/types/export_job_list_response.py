# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExportJobListResponse", "ExportJobListResponseItem"]


class ExportJobListResponseItem(BaseModel):
    id: int

    created_at: datetime = FieldInfo(alias="createdAt")

    ctms_site_id: str = FieldInfo(alias="ctmsSiteId")

    error_count: int = FieldInfo(alias="errorCount")

    in_progress_count: int = FieldInfo(alias="inProgressCount")

    site_id: int = FieldInfo(alias="siteId")

    study_id: str = FieldInfo(alias="studyId")

    success_count: int = FieldInfo(alias="successCount")

    total_exports: int = FieldInfo(alias="totalExports")

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)


ExportJobListResponse: TypeAlias = List[ExportJobListResponseItem]
