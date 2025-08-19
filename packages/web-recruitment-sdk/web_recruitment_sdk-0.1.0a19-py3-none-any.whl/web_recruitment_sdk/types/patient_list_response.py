# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .patient_read import PatientRead

__all__ = ["PatientListResponse"]

PatientListResponse: TypeAlias = List[PatientRead]
