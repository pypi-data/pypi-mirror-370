# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .export_status import ExportStatus

__all__ = ["PatientGetExportsResponse", "PatientGetExportsResponseItem"]


class PatientGetExportsResponseItem(BaseModel):
    id: int

    created_at: datetime = FieldInfo(alias="createdAt")

    ctms_site_id: str = FieldInfo(alias="ctmsSiteId")

    export_job_id: int = FieldInfo(alias="exportJobId")

    site_id: int = FieldInfo(alias="siteId")

    status: ExportStatus

    study_id: str = FieldInfo(alias="studyId")

    updated_at: datetime = FieldInfo(alias="updatedAt")


PatientGetExportsResponse: TypeAlias = List[PatientGetExportsResponseItem]
