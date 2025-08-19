# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .criteria_read import CriteriaRead

__all__ = ["CriterionRetrieveResponse"]

CriterionRetrieveResponse: TypeAlias = List[CriteriaRead]
