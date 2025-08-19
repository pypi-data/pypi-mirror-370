# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .patient_match import PatientMatch

__all__ = ["CustomSearchRetrieveMatchesResponse"]

CustomSearchRetrieveMatchesResponse: TypeAlias = List[PatientMatch]
