# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .export_status import ExportStatus

__all__ = ["SystemPatchPatientExportResponse"]


class SystemPatchPatientExportResponse(BaseModel):
    export_job_id: int = FieldInfo(alias="exportJobId")

    status: ExportStatus

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")

    id: Optional[int] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    ctms_patient_id: Optional[str] = FieldInfo(alias="ctmsPatientId", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
