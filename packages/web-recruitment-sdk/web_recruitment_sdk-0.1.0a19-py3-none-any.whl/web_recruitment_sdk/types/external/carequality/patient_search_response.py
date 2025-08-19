# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PatientSearchResponse"]


class PatientSearchResponse(BaseModel):
    carequality_patient_id: Optional[str] = FieldInfo(alias="carequalityPatientId", default=None)
    """The encrypted CareQuality patient ID (format: encrypted(tenant:patient_id))"""

    detail: Optional[str] = None
    """The detail of the response"""
