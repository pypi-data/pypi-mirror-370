# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Appointment"]


class Appointment(BaseModel):
    date: datetime

    trially_appointment_id: str = FieldInfo(alias="triallyAppointmentId")

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")
