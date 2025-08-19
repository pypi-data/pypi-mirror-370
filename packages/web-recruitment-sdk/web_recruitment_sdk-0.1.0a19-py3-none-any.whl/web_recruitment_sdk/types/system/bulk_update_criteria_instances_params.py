# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from ..criteria_instance_create_param import CriteriaInstanceCreateParam

__all__ = ["BulkUpdateCriteriaInstancesParams"]


class BulkUpdateCriteriaInstancesParams(TypedDict, total=False):
    body: Required[Iterable[CriteriaInstanceCreateParam]]
