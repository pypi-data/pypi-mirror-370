# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExportJobCreateResponse"]


class ExportJobCreateResponse(BaseModel):
    id: int

    ctms_site_id: str = FieldInfo(alias="ctmsSiteId")

    failed_exports: int = FieldInfo(alias="failedExports")

    site_id: int = FieldInfo(alias="siteId")

    skipped_exports: int = FieldInfo(alias="skippedExports")

    study_id: str = FieldInfo(alias="studyId")

    successful_exports: int = FieldInfo(alias="successfulExports")

    user_id: int = FieldInfo(alias="userId")

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)
