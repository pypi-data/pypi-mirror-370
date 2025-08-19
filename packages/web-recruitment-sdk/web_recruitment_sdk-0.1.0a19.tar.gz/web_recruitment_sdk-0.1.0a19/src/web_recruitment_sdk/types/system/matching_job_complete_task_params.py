# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..criteria_instance_create_param import CriteriaInstanceCreateParam

__all__ = ["MatchingJobCompleteTaskParams"]


class MatchingJobCompleteTaskParams(TypedDict, total=False):
    criteria_instances: Required[
        Annotated[Iterable[CriteriaInstanceCreateParam], PropertyInfo(alias="criteriaInstances")]
    ]

    task_id: Required[Annotated[int, PropertyInfo(alias="taskId")]]
    """The ID of the task as it exists in the database"""

    task_name: Required[Annotated[str, PropertyInfo(alias="taskName")]]
    """The name of the task"""

    body_tenant_db_name: Required[Annotated[str, PropertyInfo(alias="tenantDbName")]]
